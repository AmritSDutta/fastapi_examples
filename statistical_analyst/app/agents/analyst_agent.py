import html
import logging
import mimetypes
import os
import tempfile
import time
from datetime import datetime
from google import genai
from google.genai import types
from app.config.logging_config import setup_logging

setup_logging()
_llm_client = genai.Client()


# -----------------------
# Docker Note: python:slim lacks MIME mappings for .xlsx/.xls/.csv, causing FileSearch uploads to fail.
# Explicitly register these types so mimetypes.guess_type() works consistently across all platforms.
# -----------------------------------------------------------------------------------------
mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")
mimetypes.add_type("application/vnd.ms-excel", ".xls")
mimetypes.add_type("text/csv", ".csv")
# -----------------------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are an expert statistical analysis assistant.
Filestore has XLSX files containing quantitative data and expects accurate, succinct
professional-grade statistical insights.

Your role:
- Perform detailed statistical analysis on the uploaded datasets.
- Derive and verify all calculations with precision — no estimation or rounding errors.
- Respond succinctly and analytically, avoiding verbosity or narrative explanations.
- Present numeric outputs, correlations, and inferences clearly, with minimal text.
- Highlight anomalies, trends, and key metrics directly relevant to the user’s query.
- When unsure of context, ask a clarifying question before proceeding with analysis.
- Never include filler text such as “Here’s the result” or “As an AI model...”.
- Add a small not to specify which tools and method you used to come up to the solution.
- use tabular format to answer if it is necessary and it is concise.
- only provide explanation briefly if asked with reference.

constraint:
- you can not do any mathematical or statistical error or judgement.
- you will always pick right methodologies, tools for depending on specific questions.
- Must include not more than 50 words to mention tools, methods used for getting the response.

Always assume the dataset is already present in the FileSearch store.
Your output must be concise, technically correct, and quantitatively validated.
"""


def safe_call(func, *args, **kwargs):
    """Call func; on 429/503 wait 60s and retry once; log events."""
    for attempt in (1, 2):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            s = str(e)
            if ("429" in s) or ("503" in s) or getattr(e, "status_code", None) in (429, 503):
                logging.warning("Transient API error (attempt %d): %s", attempt, s)
                if attempt == 1:
                    time.sleep(60)
                    continue
            logging.error("Error calling %s: %s", getattr(func, "__name__", "<call>"), s)
            raise


def safe_delete():
    """Delete existing file_search stores (retries on transient errors)."""
    logging.info("-" * 100)
    logging.info('Started cleaning up stale uploaded files ...')
    for attempt in (1, 2):
        try:
            for file_search_store in _llm_client.file_search_stores.list():
                logging.info(f"Stale file_search_store: {file_search_store}")
                _llm_client.file_search_stores.delete(name=file_search_store.name, config={'force': True})

            logging.info("-" * 100)
            return True
        except Exception as e:
            s = str(e)
            if ("429" in s) or ("503" in s) or getattr(e, "status_code", None) in (429, 503):
                logging.warning("Transient API error (attempt %d): %s", attempt, s)
                if attempt == 1:
                    time.sleep(60)
                    continue
            logging.error("Error calling safe_delete: %s", s)
            raise


def create_store_and_upload(uploaded_files, display_name_prefix="upload-dir"):
    """Create a file_search store and upload files. Returns store object."""
    logging.info("-" * 100)
    safe_delete()
    logging.info('Creating file store and uploading files ...')

    store = safe_call(_llm_client.file_search_stores.create, config={"display_name": display_name_prefix})
    for f in uploaded_files:
        local_path = f.name
        display = getattr(f, "filename", None) or os.path.basename(local_path)
        logging.info(f"local_path={local_path}, display={display}")
        op = safe_call(_llm_client.file_search_stores.upload_to_file_search_store,
                       file=local_path,
                       file_search_store_name=store.name,
                       config={"display_name": display})
        # wait until import completes (poll)
        while not safe_call(lambda o: _llm_client.operations.get(o), op).done:
            time.sleep(2)
    logging.info("-" * 100)
    return store


def start_chat_with_store(store_name, model="gemini-2.5-flash"):
    """Create a chat bound to the given file_search store and system prompt."""
    logging.info("-" * 100)
    logging.info(f'Initializing chat with {store_name}')
    chat = safe_call(_llm_client.chats.create,
                     model=model,
                     config=types.GenerateContentConfig(
                         system_instruction=SYSTEM_PROMPT,
                         tools=[types.Tool(file_search=types.FileSearch(file_search_store_names=[store_name]))]
                     ))
    logging.info("-" * 100)
    return chat


def upload_and_start(files, model_name: str = 'gemini-2.5-flash'):
    """Uploads files, creates store and chat. Returns (status_msg, chat_obj, store_name)."""
    if not files:
        return "No files uploaded.", None, None
    try:
        store = create_store_and_upload(files, model_name)
    except Exception as e:
        return f"Upload failed: {e}", None, None
    chat = start_chat_with_store(store.name, model_name)
    return f"Uploaded {len(files)} files to {store.name}. Chat ready.", chat, store.name


def close_and_cleanup(messages):
    """
    Do cleanup (delete stores), write conversation markdown.
    Returns plain primitives (no gr.update calls).
    """
    logging.info("-" * 100)
    logging.info('cleaning up chat session..')
    try:
        safe_delete()
        status = "Session closed. Cleanup attempted."
    except Exception as e:
        logging.exception("safe_delete failed")
        status = f"Session closed. cleanup error: {e}"

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"Conversation-{timestamp}.md"
    logging.info(f'created file to save chats : {filename}')
    md_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            if messages:
                for m in messages:
                    role = (m.get("role", "") or "").capitalize()
                    content = html.unescape(str(m.get("content", "")))
                    f.write(f"**{role}:**\n\n{content}\n\n---\n")
            else:
                f.write("# Conversation\n\n(no messages)\n")
    except Exception:
        logging.exception("Failed to build/write Conversation.md")
        raise
    logging.info("-" * 100)

    # Return plain, gradio-agnostic values
    return (
        md_path,  # path to markdown file
        False,  # uploader interactive (False -> disabled)
        "",  # user_msg value (cleared)
        False,  # send_btn interactive
        False,  # btn_upload interactive
        False,  # btn_close interactive
        [],  # chat_box messages cleared
        status,  # out_text status message
        None,  # state_chat cleared
        None,  # state_store cleared
        []  # state_messages cleared
    )
