# analyst_gradio_ui.py — Gradio UI, converts agent primitives -> gr.update(...)
import gradio as gr
import logging

from app.agents.analyst_agent import upload_and_start, safe_call, close_and_cleanup

USER_AVATAR = "👤"
ASSISTANT_AVATAR = "🤖"

with gr.Blocks() as demo:
    gr.Markdown("🤖 Multi-file Statistical Analysis Agent 🤖")
    uploader = gr.File(file_count="multiple", label="Upload XLSX / CSV / TXT files")
    out_text = gr.Textbox(label="Status", interactive=False)

    # persistent states
    state_chat = gr.State(None)  # stores chat object
    state_store = gr.State(None)  # stores file search store name
    state_messages = gr.State([])  # conversation history

    btn_upload = gr.Button("Upload & Start Chat")
    chat_box = gr.Chatbot(type="messages", avatar_images=None, label="Chat")
    user_msg = gr.Textbox(placeholder="Ask about the uploaded files...", lines=2)
    send_btn = gr.Button("Send", interactive=False)
    btn_close = gr.Button("Close Chat", variant="stop")
    download_md = gr.File(label="Conversation.md", visible=False, elem_id='download_md')


    def on_upload(files):
        # agent.upload_and_start returns plain (msg, chat_obj, store_name)
        msg, chat_obj, store_name = upload_and_start(files)
        send_btn_update = gr.update(interactive=True) if chat_obj else gr.update(interactive=False)
        # return values: out_text, state_chat, state_store, state_messages, send_btn
        logging.info(f'Files uploaded')
        return msg, chat_obj, store_name, [], send_btn_update


    btn_upload.click(on_upload, inputs=[uploader],
                     outputs=[out_text, state_chat, state_store, state_messages, send_btn])


    def send_message(user_q, chat_obj, messages):
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
            resp = safe_call(chat_obj.send_message, user_q)
            text = getattr(resp, "text", str(resp))
            logging.info(f'response snippet: {text[:100]}')
        except Exception as e:
            text = f"ERROR: {e}"
        messages += [{"role": "assistant", "content": text, "avatar": ASSISTANT_AVATAR, "name": "Analyst"}]
        logging.info("-" * 100)
        return gr.update(value=messages), "", messages


    send_btn.click(send_message, inputs=[user_msg, state_chat, state_messages],
                   outputs=[chat_box, out_text, state_messages])


    def close_and_cleanup_ui(messages):
        """
        Wrap agent.close_and_cleanup (which returns primitives) and convert into gr.update outputs.
        Outputs match the btn_close.click wiring below.
        """
        logging.info(f'Started session shutting down')

        (md_path, uploader_i, user_msg_v, send_btn_i, btn_upload_i, btn_close_i,
         chatbox_v, status, state_chat_v, state_store_v, state_messages_v) = close_and_cleanup(messages)

        return (
            gr.update(value=md_path, visible=True),  # download_md
            gr.update(interactive=uploader_i),  # uploader
            gr.update(value=user_msg_v),  # user_msg
            gr.update(interactive=send_btn_i),  # send_btn
            gr.update(interactive=btn_upload_i),  # btn_upload
            gr.update(interactive=btn_close_i),  # btn_close
            gr.update(value=chatbox_v),  # chatbox
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
    logging.info(f' Finishing session shutting down')

if __name__ == "__main__":
    demo.launch()
