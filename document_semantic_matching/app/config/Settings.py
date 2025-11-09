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
    DB_NAME: str = 'wine_review_gemini'
    DB_USER: str = 'user'
    DB_PASSWORD: str = 'password'
    CSV_FILE: str = 'data/wine_reviews.csv'
    BATCH_SIZE: int = 10
    SLEEP_BETWEEN_BATCHES: int = 2

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent  # points to project_root

    @property
    def csv_file_path(self) -> Path:
        """Return absolute, validated path to the CSV."""
        path = self.BASE_DIR / self.CSV_FILE
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found at {path}")
        return path

    class Config:
        env_file = DOTENV_PATH  # Path to your .env file
        env_file_encoding = "utf-8"


_settings: Settings | None = None  # Singleton instance


def get_settings() -> Settings:
    global _settings

    if _settings is None:
        _settings = Settings()  # create instance
        logging.info("Settings Loaded")

        # Lazy init only once
        print(DOTENV_PATH)

        logging.info(f"CWD: {os.getcwd()}")
        logging.info(f"model_dump: {_settings.model_dump()}")

    return _settings
