import html
import re

from fastapi import HTTPException

MALICIOUS_PATTERNS = [
    r"(?i)\b(eval|exec|__import__|os\.system|subprocess|popen|open)\b",
    r"(<script\b|javascript:|on\w+\=)",  # XSS
    r"(\.\./|\.\.\\|/etc/|C:\\Windows\\System32)",  # path-traversal
]


def sanitize_passage(p: str, max_len=5000):
    if not isinstance(p, str):
        raise HTTPException(400, "Invalid type")
    p = p.strip()
    if not p:
        raise HTTPException(400, "Empty passage")
    if len(p) > max_len:
        raise HTTPException(413, "Payload too large")
    # reject binary / non-utf text
    try:
        p.encode("utf-8")
    except Exception:
        raise HTTPException(400, "Invalid encoding")
    # neutralize HTML
    p = html.escape(p)
    # pattern checks (catch obvious and obfuscated attempts)
    clean = re.sub(r"[\u200B-\u200D\uFEFF]", "", p)  # remove zero-width
    for pat in MALICIOUS_PATTERNS:
        if re.search(pat, clean):
            raise HTTPException(400, "Malicious content detected")
    return clean
