"""
Rate limiting and security utilities for TabSense API.
Uses slowapi (built on `limits`) for per-IP rate limiting.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter — key by client IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],          # Global ceiling for all routes
    headers_enabled=False,                  # Disabled: requires Response param in every route
)

# Named limit strings for reuse across routes
LIMITS = {
    "default":      "200/minute",
    "write":        "60/minute",            # POST/PATCH/DELETE mutations
    "ai":           "20/minute",            # Gemini calls are expensive
    "sensitive":    "5/15minutes",          # Login-equivalent endpoints
    "inactivity":   "30/minute",            # Polling endpoint
}
