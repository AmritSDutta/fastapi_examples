import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DOTENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=DOTENV_PATH)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    APP_NAME: str = 'Document Search App1'
    PORT: int = 8000
    TABLE_NAME: str = 'wines_3'
    EMBED_DIM: int = 256
    DB_DSN: str = 'postgres://user:password@localhost/wine_review_gemini'
    EMBEDDING_MODEL: str = 'models/text-embedding-004'

    class Config:
        env_file = DOTENV_PATH  # Path to your .env file
        env_file_encoding = "utf-8"


_settings = Settings()  # Singleton instance


def get_settings() -> Settings:
    print(DOTENV_PATH)

    logging.info('Setting Loaded')
    logging.info(f"CWD: {os.getcwd()}")
    logging.info(f"model_dump: {_settings.model_dump()}")
    return _settings



