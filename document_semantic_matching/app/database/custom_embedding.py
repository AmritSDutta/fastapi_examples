import json
import time
from google import genai
from app.config.Settings import get_settings


def get_gemini_embedding(input_sentence: str, specific_task_type: str = 'semantic_similarity', dim: int = 256):
    """Return a flattened embedding vector (for pgvector, etc.) using Gemini."""
    max_retries = 3
    backoff = 1.0
    client = genai.Client()
    for attempt in range(max_retries):
        try:
            result = client.models.embed_content(
                model=get_settings().EMBEDDING_MODEL,
                contents=[input_sentence],
                config={
                    "task_type": specific_task_type,
                    "output_dimensionality": dim
                }
            )
            # result.embeddings or result.embedding? inspect SDK response
            return result.embeddings[0].values

        except Exception as e:

            print("Rate limit hit (attempt %d/%d)" % (attempt + 1, max_retries))
            print("Error message:", e.message if hasattr(e, "message") else str(e))
            # Headers are attached in e.response if available
            if hasattr(e, "response") and hasattr(e.response, "headers"):
                headers = e.response.headers
                print("---- Rate limit details ----")
                for k, v in headers.items():
                    if "rate" in k.lower() or "quota" in k.lower():
                        print(f"{k}: {v}")
                print("----------------------------")

            # Full raw response for debugging (optional)
            if hasattr(e, "response") and hasattr(e.response, "text"):
                try:
                    err_json = json.loads(e.response.text)
                    print("Error JSON:", json.dumps(err_json, indent=2))
                except Exception as e:
                    print("Raw error text:", e.response.text)

            # Backoff before retry

            if attempt < max_retries - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise e
