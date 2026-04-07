"""Input sanitization utilities for preventing injection attacks."""

import html
import re
from typing import Any


# Patterns that indicate potential injection attempts
SQL_INJECTION_PATTERNS = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|UNION|;)\b)",
    re.IGNORECASE,
)

# Dangerous characters in path traversal
PATH_TRAVERSAL_PATTERN = re.compile(r"\.\./|\.\.\\|%2e%2e|%252e")

# Control characters (except \n, \r, \t which are valid in text)
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_html(value: str) -> str:
    """Escape HTML entities to prevent XSS in user-provided content."""
    return html.escape(value, quote=True)


def strip_control_chars(value: str) -> str:
    """Remove control characters that could cause parsing issues."""
    return CONTROL_CHARS.sub("", value)


def sanitize_text_input(value: str, max_length: int = 10000) -> str:
    """
    Sanitize a general text input.

    - Strips control characters
    - Trims to max length
    - Strips leading/trailing whitespace
    """
    value = strip_control_chars(value)
    value = value.strip()
    return value[:max_length]


def sanitize_identifier(value: str) -> str:
    """
    Sanitize a value intended for use as an identifier (slugs, keys, etc.).

    Only allows alphanumeric, hyphens, and underscores.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", value)


def check_path_traversal(value: str) -> bool:
    """Return True if the value contains path traversal patterns."""
    return bool(PATH_TRAVERSAL_PATTERN.search(value))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe storage.

    - Removes path separators
    - Only allows safe characters
    - Limits length
    """
    # Remove any directory components
    filename = filename.replace("/", "").replace("\\", "")
    # Remove control chars
    filename = strip_control_chars(filename)
    # Keep only safe characters
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    # Limit length
    return filename[:255]


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """
    Mask a sensitive value, showing only the last N characters.

    Example: mask_sensitive("np_live_alpha_abc123") -> "••••••••••••••c123"
    """
    if len(value) <= visible_chars:
        return "•" * len(value)
    masked_len = len(value) - visible_chars
    return "•" * masked_len + value[-visible_chars:]


def sanitize_log_value(value: Any) -> Any:
    """
    Sanitize a value before including it in log output.

    Prevents sensitive data from leaking into logs.
    """
    if isinstance(value, str):
        # Mask anything that looks like an API key
        if value.startswith("np_"):
            return mask_sensitive(value)
        # Mask JWT tokens
        if value.startswith("eyJ"):
            return mask_sensitive(value, 8)
        # Limit very long strings
        if len(value) > 500:
            return value[:500] + "...[truncated]"
    return value
