import logging
import sys

LEVEL_COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[1;31m",  # Bold Red
}
RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{RESET}"
        return super().format(record)


def setup_logging():
    # Skip configuration if logging already initialized (e.g., by Uvicorn)
    root = logging.getLogger()
    if root.handlers:
        return

    LOG_FORMAT = (
        "%(asctime)s.%(msecs)03d | %(levelname)-8s | "
        "%(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"
    )
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter(LOG_FORMAT, DATE_FORMAT))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
