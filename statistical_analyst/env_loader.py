import os

from attr.converters import to_bool
from dotenv import load_dotenv


def load_env():
    """
    Loads environment variables from .env file
    """
    load_dotenv()  # loads .env into environment

    config = {
        "MODEL_NAME": os.getenv("MODEL_NAME", "gemini-2.5-flash-lite"),  # default fallback
        "INPUT_VALIDATION_MODEL": os.getenv("INPUT_VALIDATION_MODEL", "gemini-2.5-flash-lite"),  # default fallback
        "CHAT_INPUT_VALIDATION_REQUIRED": to_bool(
            os.getenv("CHAT_INPUT_VALIDATION_REQUIRED", "False")
        )
    }

    return config
