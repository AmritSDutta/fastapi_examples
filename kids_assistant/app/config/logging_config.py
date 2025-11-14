import logging
import sys


def setup_logging(level=logging.INFO):
    """Initialize contextual, structured logging for the whole app."""
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(funcName)s(): %(lineno)d | %(message)s "

    )

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Suppress noisy libs
    for noisy in ("uvicorn", "fastapi", "asyncio", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.info("Global logging initialized with trace context support")
