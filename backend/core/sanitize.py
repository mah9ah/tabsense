"""
Input sanitization helpers.
Applied at the schema layer — rejects or cleans malicious/oversized input
before it ever reaches the database or AI service.
"""
import re
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────────────
MAX_TITLE_LEN   = 512
MAX_URL_LEN     = 2048
MAX_APP_LEN     = 256
MAX_DETAILS_LEN = 4096
MAX_SEARCH_LEN  = 200

# Basic URL pattern — allows http/https only (no javascript:, data:, etc.)
_SAFE_URL_RE = re.compile(
    r'^https?://'                 # must start with http:// or https://
    r'[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+'
    r'$',
    re.IGNORECASE,
)

# Strip anything that looks like an HTML tag or script injection
_HTML_TAG_RE = re.compile(r'<[^>]*>', re.IGNORECASE)

# Null byte — always reject
_NULL_BYTE_RE = re.compile(r'\x00')


def strip_html(value: str) -> str:
    """Remove HTML/script tags from a string."""
    return _HTML_TAG_RE.sub('', value).strip()


def reject_null_bytes(value: str, field: str = "field") -> str:
    if _NULL_BYTE_RE.search(value):
        raise ValueError(f"{field} contains invalid characters.")
    return value


def sanitize_text(value: Optional[str], max_len: int, field: str = "value") -> Optional[str]:
    """Strip HTML, reject null bytes, enforce max length."""
    if value is None:
        return None
    value = reject_null_bytes(value, field)
    value = strip_html(value)
    if len(value) > max_len:
        raise ValueError(f"{field} exceeds maximum length of {max_len} characters.")
    return value


def sanitize_url(value: Optional[str]) -> Optional[str]:
    """Validate and sanitize a URL — only http/https allowed."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    reject_null_bytes(value, "url")
    if len(value) > MAX_URL_LEN:
        raise ValueError(f"URL exceeds maximum length of {MAX_URL_LEN} characters.")
    if not _SAFE_URL_RE.match(value):
        raise ValueError("URL must start with http:// or https:// and contain only valid characters.")
    return value
