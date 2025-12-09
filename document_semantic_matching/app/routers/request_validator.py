import html
import logging
import re

from fastapi import HTTPException
from openai import OpenAI, RateLimitError, APIError, APIConnectionError

MALICIOUS_PATTERNS = [
    r"(?i)\b(eval|exec|__import__|os\.system|subprocess|popen|open)\b",
    r"(<script\b|javascript:|on\w+\=)",  # XSS
    r"(\.\./|\.\.\\|/etc/|C:\\Windows\\System32)",  # path-traversal
]


def sanitize_passage(user_input: str, max_len=5000):
    if not isinstance(user_input, str):
        raise HTTPException(400, "Invalid type")
    user_input = user_input.strip()
    if not user_input:
        raise HTTPException(400, "Empty passage")
    if len(user_input) > max_len:
        raise HTTPException(413, "Payload too large")
    # reject binary / non-utf text
    try:
        user_input.encode("utf-8")
    except Exception:
        raise HTTPException(400, "Invalid encoding")
    # neutralize HTML
    user_input = html.escape(user_input)
    # pattern checks (catch obvious and obfuscated attempts)
    clean = re.sub(r"[\u200B-\u200D\uFEFF]", "", user_input)  # remove zero-width
    for pat in MALICIOUS_PATTERNS:
        if re.search(pat, clean):
            raise HTTPException(400, "Malicious content detected")
    return clean


def do_moderation_checking(user_input: str) -> None:
    """
    last frontier , check with LLM moderation model
    """
    logging.info('starting moderation checking')
    client = OpenAI()

    try:
        resp = client.moderations.create(
            model="omni-moderation-latest",
            input=user_input
        )

        if any(result.flagged for result in resp.results):
            logging.info('moderation check failed:{}'.format(resp))
            raise HTTPException(status_code=403, detail="Malicious content detected")

    except RateLimitError:
        # Fail closed (block the request)
        raise HTTPException(status_code=429, detail="Moderation rate limit hit")

    except (APIError, APIConnectionError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Moderation service unavailable: {e}"
        )