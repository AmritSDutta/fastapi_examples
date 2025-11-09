import json
import time

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

EMBEDDING_MODEL = "models/text-embedding-004"


def get_gemini_embedding(input_sentence: str, specific_task_type: str = 'semantic_similarity', dim: int = 256):
    """Return a flattened embedding vector (for pgvector, etc.) using Gemini."""
    max_retries = 3
    backoff = 1.0

    for attempt in range(max_retries):
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=input_sentence,
                task_type=specific_task_type,
                output_dimensionality=dim
            )
            return result["embedding"]

        except ResourceExhausted as e:

            print("\n⚠️  Rate limit hit (attempt %d/%d)" % (attempt + 1, max_retries))
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
