import html
import logging
import os
import tempfile
import time
from datetime import datetime

import gradio as gr
from google import genai
from google.genai import types

from app.config.logging_config import setup_logging

setup_logging()

client = genai.Client()  # configure env vars / ADC or pass project/location if required
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
    """Call func, on 429/503 wait 60s and retry once; log events."""
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
    """Call func, on 429/503 wait 60s and retry once; log events."""
    for attempt in (1, 2):
        try:
            for file_search_store in client.file_search_stores.list():
                logging.info(f"Stale file_search_store: {file_search_store}")
                client.file_search_stores.delete(name=file_search_store.name,
                                                 config={'force': True})
                logging.info("-" * 50)
        except Exception as e:
            s = str(e)
            if ("429" in s) or ("503" in s) or getattr(e, "status_code", None) in (429, 503):
                logging.warning("Transient API error (attempt %d): %s", attempt, s)
                if attempt == 1:
                    time.sleep(60)
                    continue
            logging.error("Error calling safe_delete", s)
            raise


def create_store_and_upload(uploaded_files):
    # create unique store
    safe_delete()
    store = safe_call(client.file_search_stores.create, config={"display_name": "upload-dir"})
    for f in uploaded_files:
        # f is a tempfile-like object from gradio; write to disk then upload
        local_path = f.name
        display = os.path.basename(local_path)
        op = safe_call(client.file_search_stores.upload_to_file_search_store,
                       file=local_path,
                       file_search_store_name=store.name,
                       config={"display_name": display})
        # wait until import completes (poll)
        while not safe_call(lambda o: client.operations.get(o), op).done:
            time.sleep(2)
    return store


def start_chat_with_store(store_name):
    logging.info(f'Initializing chat with  {store_name}')
    chat = safe_call(client.chats.create,
                     model="gemini-2.5-flash",
                     config=types.GenerateContentConfig(
                         system_instruction=SYSTEM_PROMPT,
                         tools=[types.Tool(file_search=types.FileSearch(file_search_store_names=[store_name]))]
                     ))
    return chat


def upload_and_start(files):
    if not files:
        return "No files uploaded.", None, None
    try:
        store = create_store_and_upload(files)
    except Exception as e:
        return f"Upload failed: {e}", None, None
    chat = start_chat_with_store(store.name)
    return f"Uploaded {len(files)} files to {store.name}. Chat ready.", chat, store.name


# wire this as the close handler
def close_and_cleanup(messages):
    try:
        safe_delete()
        status = "Session closed. Cleanup attempted."
    except Exception as e:
        logging.exception("safe_delete failed")
        status = f"Session closed. cleanup error: {e}"

    # Build timestamped filename in temp dir
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"Conversation-{timestamp}.md"
        md_path = os.path.join(tempfile.gettempdir(), filename)

        # Write Markdown content
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

    # Return values must match outputs:
    return (
        md_path,                         # download_md (path string) -> will download as Conversation-<ts>.md
        gr.update(interactive=False),    # uploader disabled
        gr.update(value=""),             # user_msg cleared
        gr.update(interactive=False),    # send_btn disabled
        gr.update(interactive=False),    # btn_upload disabled
        gr.update(interactive=False),    # btn_close disabled
        gr.update(value=[]),             # chatbox cleared
        status,                          # out_text message
        None,                            # state_chat cleared
        None,                            # state_store cleared
        []                               # state_messages cleared
    )


# --- Updated Gradio UI (drop this into your script) ---
with gr.Blocks() as demo:
    gr.Markdown("### Multi-file Statistical Analysis Agent (Gemini + FileSearch)")

    uploader = gr.File(file_count="multiple", label="Upload XLSX / CSV / TXT files")
    out_text = gr.Textbox(label="Status", interactive=False)

    # persistent states
    state_chat = gr.State(None)  # stores chat object
    state_store = gr.State(None)  # stores file search store name
    state_messages = gr.State([])  # stores conversation history

    btn_upload = gr.Button("Upload & Start Chat")

    # avatars (emoji or HTTPS image URLs)
    USER_AVATAR = "👤"
    ASSISTANT_AVATAR = "🤖"
    # Chat UI
    chatbox = gr.Chatbot(type="messages", avatar_images=None, label="Chat")
    user_msg = gr.Textbox(placeholder="Ask about the uploaded files...", lines=2)
    send_btn = gr.Button("Send", interactive=False)
    btn_close = gr.Button("Close Chat", variant="stop")
    download_md = gr.File(label="Conversation.md", visible=False, elem_id='download_md')

    def on_upload(files):
        """
        upload handler (expects upload_and_start(...) available)
       """
        msg, chat_obj, store_name = upload_and_start(files)
        send_btn = gr.update(interactive=True)
        return msg, chat_obj, store_name, [], send_btn  # reset messages on new upload


    btn_upload.click(on_upload, inputs=[uploader],
                     outputs=[out_text, state_chat, state_store, state_messages, send_btn])


    def send_message(user_q, chat_obj, messages):
        """
        send handler (uses safe_call and chat object)
        :param user_q:
        :param chat_obj:
        :param messages:
        :return:
        """
        if not chat_obj:
            return gr.update(), "No active chat. Upload files first.", messages
        user_q = (user_q or "").strip()
        if not user_q:
            return gr.update(), "", messages
        logging.info(f'query: {user_q[:100]} ....')
        # append user message
        messages = (messages or []) + [{"role": "user", "content": user_q, "avatar": USER_AVATAR, "name": "You"}]
        try:
            resp = safe_call(chat_obj.send_message, user_q)
            text = getattr(resp, "text", str(resp))
            logging.info(f'response: {text[:100]} ...')
        except Exception as e:
            text = f"ERROR: {e}"
        messages += [{"role": "assistant", "content": text, "avatar": ASSISTANT_AVATAR, "name": "Analyst"}]
        logging.info("-" * 50)
        return gr.update(value=messages), "", messages


    send_btn.click(send_message, inputs=[user_msg, state_chat, state_messages],
                   outputs=[chatbox, out_text, state_messages])


    def close_chat(messages):
        """
        close handler: clear states and disable inputs (no tab-closing JS)
        :param messages:
        :return:
        """
        return None, None, [], gr.update(value=[]), "Session closed."


    # Wire into UI (ensure outputs order matches the tuple above)
    btn_close.click(close_and_cleanup, inputs=[state_messages],
                    outputs=[download_md, uploader, user_msg, send_btn, btn_upload, btn_close, chatbox,
                             out_text, state_chat, state_store, state_messages],
                    js="""
                    () => {
                              const start = Date.now();
                              const maxMs = 5000;
                              const interval = 150;
                            
                              const poll = setInterval(() => {
                                const mdLink = document.querySelector('#download_md a[download]');
                            
                                if (mdLink) {
                                  mdLink.click();          // ⬅️ starts the download instantly
                                  clearInterval(poll);
                                } 
                                else if (Date.now() - start > maxMs) {
                                  clearInterval(poll);
                                }
                              }, interval);
                    }

                    """
                    )

if __name__ == "__main__":
    demo.launch()
