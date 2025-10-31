import logging
import os
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=DOTENV_PATH)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    APP_NAME: str = "App"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    LOG_FORMAT: str = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

    class Config:
        env_file = "../.env"  # Path to your .env file
        env_file_encoding = "utf-8"


settings = Settings()  # Singleton instance


def get_settings() -> Settings:
    print("model_dump:", settings.model_dump())

    # Configure logging using the LOG_LEVEL and LOG_FORMAT from settings
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format=settings.LOG_FORMAT
    )
    logging.info('Setting Loaded')
    logging.info(f"CWD: {os.getcwd()}")
    logging.info(f"model_dump: {settings.model_dump()}")
    return settings


def get_run_id(run_type: str = 'train') -> str:
    # --- Unique Run Name ---
    run_id = str(uuid.uuid4())[:8]  # short unique id
    run_name = f"{run_type}-{time.strftime('%Y-%m-%dT%H.%M.%S')}-{run_id}"
    return run_name
