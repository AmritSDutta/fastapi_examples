import gradio as gr
import logging

from app.agents.analyst_agent import upload_and_start, safe_call, close_and_cleanup
from app.agents.data_models import ValidatorResponse
from env_loader import load_env

config = load_env()
MODEL_NAME = config["MODEL_NAME"]
CHAT_INPUT_VALIDATION_REQUIRED: bool = config["CHAT_INPUT_VALIDATION_REQUIRED"]
ALLOWED_FILE_TYPES = {".xlsx", ".xls", ".csv"}
DEFAULT_HINT = "Ask about the uploaded files..."

USER_AVATAR = "👤"
ASSISTANT_AVATAR = "🤖"

logging.basicConfig(level=logging.INFO)

with gr.Blocks() as demo:
    gr.Markdown("🤖 Multi-file Statistical Analysis Agent 🤖")

    gr.HTML("""
    <style>
    #chat_box_area {
        height: 65vh !important;   /* You can tune to 70–85vh */
        max-height: 75vh !important;
    }
    </style>
    """)
    # Layout: Row with two columns (scale 3 : 7 => ~30% : 70%)
    with gr.Row():
        # LEFT column (30%) — uploader + upload button + status
        with gr.Column(scale=3):
            uploader = gr.File(file_count="multiple", label="Upload XLSX / CSV / TXT files")
            btn_upload = gr.Button("Upload & Start Chat")
            out_text = gr.Textbox(label="Status", interactive=False)
            # Keep download file hidden here (will be made visible on close)
            download_md = gr.File(label="Conversation.md",
                                  visible=False,
                                  file_types=[".xlsx", ".xls", ".csv"],
                                  elem_id='download_md')
            btn_close = gr.Button("Close Chat", variant="stop")

        # RIGHT column (70%) — chat area + input controls
        with gr.Column(scale=7):
            chat_box = gr.Chatbot(type="messages", avatar_images=None, label="Chat", elem_id="chat_box_area")
            user_msg = gr.Textbox(placeholder=DEFAULT_HINT, lines=2)
            with gr.Row():
                send_btn = gr.Button("Send", interactive=False)

    # persistent states
    state_chat = gr.State(None)  # stores chat object
    state_store = gr.State(None)  # stores file search store name
    state_messages = gr.State([])  # conversation history
    val_chat = gr.State(None)  # stores chat object


    def on_upload(files):
        ok, msg, norm_files = _normalize_and_validate(files)
        if not ok:
            logging.warning(msg)
            return msg, None, None, [], gr.update(interactive=False), None
        msg, chat_obj, store_name, validator_agent = upload_and_start(files, MODEL_NAME)
        send_btn_update = gr.update(interactive=True) if chat_obj else gr.update(interactive=False)
        logging.info('Files uploaded')
        # outputs: out_text, state_chat, state_store, state_messages, send_btn
        return msg, chat_obj, store_name, [], send_btn_update, validator_agent


    btn_upload.click(on_upload, inputs=[uploader],
                     outputs=[out_text, state_chat, state_store, state_messages, send_btn, val_chat])


    def send_message(user_q, chat_obj, messages, val_obj):
        logging.info("-" * 100)
        if not chat_obj:
            return gr.update(), "No active chat. Upload files first.", messages
        user_q = (user_q or "").strip()
        if not user_q:
            return gr.update(), "", messages
        logging.info(f'user query passed: {user_q}')
        # append user message to local messages
        messages = (messages or []) + [{"role": "user", "content": user_q, "avatar": USER_AVATAR, "name": "You"}]
        try:
            val_json = safe_call(val_obj.send_message, user_q)
            validation_result: ValidatorResponse = _parse_validator_json(val_json)
            if validation_result.isStatisticalQuery:
                logging.warning(f'validation fine :  {validation_result.isStatisticalQuery}')
                resp = safe_call(chat_obj.send_message, user_q)
                text = getattr(resp, "text", str(resp))
                logging.info(f'response snippet: {text[:100]}')
            else:
                text = validation_result.reason
                logging.warning(f'response snippet: {text}')

        except Exception as e:
            text = f"ERROR: {e}"
        messages += [{"role": "assistant", "content": text, "avatar": ASSISTANT_AVATAR, "name": "Analyst"}]
        logging.info("-" * 100)
        # outputs: chat_box, out_text, state_messages
        return gr.update(value=messages), "", messages, gr.update(value='')


    send_btn.click(send_message, inputs=[user_msg, state_chat, state_messages, val_chat],
                   outputs=[chat_box, out_text, state_messages, user_msg])


    def close_and_cleanup_ui(messages):
        """
        Wrap agent.close_and_cleanup (which returns primitives) and convert into gr.update outputs.
        Outputs match the btn_close.click wiring below.
        """
        logging.info('Started session shutting down')

        (md_path, uploader_i, user_msg_v, send_btn_i, btn_upload_i, btn_close_i,
         chatbox_v, status, state_chat_v, state_store_v, state_messages_v) = close_and_cleanup(messages)

        return (
            gr.update(value=md_path, visible=True),  # download_md
            gr.update(interactive=uploader_i),  # uploader
            gr.update(value=user_msg_v),  # user_msg
            gr.update(interactive=send_btn_i),  # send_btn
            gr.update(interactive=btn_upload_i),  # btn_upload
            gr.update(interactive=btn_close_i),  # btn_close
            gr.update(value=chatbox_v),  # chat_box
            status,  # out_text (plain string ok)
            state_chat_v,  # state_chat
            state_store_v,  # state_store
            state_messages_v  # state_messages
        )


    btn_close.click(close_and_cleanup_ui, inputs=[state_messages],
                    outputs=[download_md, uploader, user_msg, send_btn, btn_upload, btn_close, chat_box,
                             out_text, state_chat, state_store, state_messages],
                    js="""
                    () => {
                      const start = Date.now();
                      const maxMs = 5000;
                      const interval = 150;
                      const poll = setInterval(() => {
                        const mdLink = document.querySelector('#download_md a[download]');
                        if (mdLink) { mdLink.click(); clearInterval(poll); }
                        else if (Date.now() - start > maxMs) clearInterval(poll);
                      }, interval);
                    }
                    """)

    logging.info(' Finishing session setup')


def _normalize_and_validate(files, allowed=None):
    """
    Normalize gr.File input  extensions.
    Returns (ok:bool, msg:str, normalized_files:list).
    """
    if allowed is None:
        allowed = ALLOWED_FILE_TYPES
    if not files:
        return False, "No files selected.", []
    normalized = []
    names = []
    for f in files:
        name = getattr(f, "name", None) or (f.get("name") if isinstance(f, dict) else str(f))
        names.append(name)
        normalized.append(f)
    bad = [f'{n[:3]}...{n[-5:]}' for n in names if not any(n.lower().endswith(ext) for ext in allowed)]
    if bad:
        msg = f"Rejected: only Allowed: {', '.join(sorted(allowed))},  uploaded files (unsupported): {', '.join(bad)}. "
        return False, msg, []
    return True, "OK", normalized


def _parse_validator_json(val_json: str) -> ValidatorResponse:
    if CHAT_INPUT_VALIDATION_REQUIRED:
        val_text = getattr(val_json, "text", str(val_json))
        try:

            logging.info(f'input validator LLM response : {val_text}')
            response = ValidatorResponse.model_validate_json(val_text)
            return response
        except Exception as exc:
            logging.warning(f'input validator LLM wrong response : {val_text}, {exc}')

    return ValidatorResponse(
        isStatisticalQuery=True,
        confidence=1.0,
        reason=f"Bypassed chat input validation"
    )


if __name__ == "__main__":
    demo.launch()
