import os
from dotenv import load_dotenv


def load_env():
    """
    Loads environment variables from .env file
    """
    load_dotenv()  # loads .env into environment

    config = {
        "MODEL_NAME": os.getenv("MODEL_NAME", "gemini-2.5-flash-lite"),  # default fallback
    }

    return config
