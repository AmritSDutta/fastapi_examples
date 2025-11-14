import json
import logging
import time

import numpy as np
import os
import soundfile as sf
import tempfile

import gradio as gr
from google import genai
from gtts import gTTS
from vosk import Model, KaldiRecognizer

from app.config.logging_config import setup_logging

# ----- CONFIG -----
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_DIR", r"C:\Users\amrit\vosk_models\vosk-model-small-en-us-0.15")

setup_logging()
# Init clients/models
client = genai.Client()
if not os.path.exists(VOSK_MODEL_PATH):
    raise RuntimeError(f"Vosk model not found at {VOSK_MODEL_PATH}. Download and set VOSK_MODEL_DIR.")
vosk_model = Model(VOSK_MODEL_PATH)


# ----- Helpers -----

def _parse_audio(audio: object) -> tuple[np.ndarray | None, int | None]:
    """Return (arr: np.ndarray (1D), sr: int) or (None, None) on failure."""
    if audio is None:
        return None, None
    # filepath (gr.Audio type="filepath")
    if isinstance(audio, str):
        data, sr = sf.read(audio)
        arr = np.array(data)
    # tuple/list (common shapes: (array, sr) or (sr, array))
    elif isinstance(audio, (tuple, list)):
        a0 = audio[0] if len(audio) > 0 else None
        a1 = audio[1] if len(audio) > 1 else None
        # detect which is sample rate
        if isinstance(a0, (int, float)) and hasattr(a1, "ndim"):
            sr = int(a0)
            arr = np.array(a1)
        elif isinstance(a1, (int, float)) and hasattr(a0, "ndim"):
            sr = int(a1)
            arr = np.array(a0)
        else:
            # fallback: assume (array, sr)
            arr = np.array(a0)
            sr = int(a1) if isinstance(a1, (int, float)) else 16000
    # dict {'array':..., 'sample_rate':...}
    elif isinstance(audio, dict):
        arr = np.array(audio.get("array"))
        sr = int(audio.get("sample_rate", 16000))
    # raw numpy-like
    else:
        try:
            arr = np.array(audio)
            sr = 16000
        except Exception:
            return None, None

    # Ensure 1D mono
    if arr is None:
        return None, None
    if arr.ndim > 1:
        # average channels to mono
        arr = arr.mean(axis=1)
    return arr.astype(np.float32), int(sr)


def transcribe(filepath: str) -> str:
    if not filepath or not os.path.exists(filepath):
        print("DEBUG: filepath missing:", filepath)
        return ""

    print("received file:", filepath)

    data, sr = sf.read(filepath)

    print("raw shape=", getattr(data, "shape", None), "sr=", sr)

    # convert to mono
    if data.ndim > 1:
        data = data.mean(axis=1)

    # resample to 16k
    if sr != 16000:
        new_len = int(len(data) * 16000 / sr)
        data = np.interp(np.linspace(0, len(data), new_len),
                         np.arange(len(data)), data)
        sr = 16000

    # save normalized audio for Vosk
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, data, sr)

    logging.info("normalized wav:", tmp.name, "size:", os.path.getsize(tmp.name))

    # run Vosk
    rec = KaldiRecognizer(vosk_model, 16000)
    with open(tmp.name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            rec.AcceptWaveform(chunk)

    result = json.loads(rec.FinalResult()).get("text", "")

    logging.info("vosk text:", repr(result))

    return result


def respond(filepath: str) -> tuple[str, str | None]:
    user_text = transcribe(filepath)
    logging.info(f'transcribed audio: {user_text}')
    if not user_text:
        return "Didn't hear anything!", None
    # Fixed multiline f-string using triple quotes to avoid unterminated string errors
    prompt = f"""You are 'Upanishad', a friendly 12-year-old Indian boy. Keep replies short and kid-appropriate.
    User: {user_text}
    Assistant:"""
    # call Gemini (Client imported as genai.Client)
    llm_resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
    reply_text = getattr(llm_resp, "text", None) or getattr(llm_resp, "output", "") or str(llm_resp)
    logging.info(f'llm replies : {reply_text}')

    # TTS -> mp3 filepath for Gradio audio(type="filepath")
    tts_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    gTTS(reply_text).save(tts_file.name)
    return reply_text, tts_file.name


def _safe_call(func, *args, **kwargs):
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


# ----- UI -----
with gr.Blocks(title="Rohan — Kids Playmate") as demo:
    gr.Markdown("### **Rohan (12-year-old Indian boy)** — Speak or type to him!")

    audio_in = gr.Audio(sources=["microphone"], type="filepath", format="wav")
    text_out = gr.Textbox(label="Rohan says (text)")
    audio_out = gr.Audio(type="filepath", label="Rohan says (audio)")

    audio_in.change(fn=respond, inputs=audio_in, outputs=[text_out, audio_out])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=9000)
