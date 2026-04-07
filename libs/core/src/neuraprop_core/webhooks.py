"""Webhook signature generation and verification.

Used for securing inbound webhooks (e.g., from Veriff, payment providers)
and outbound webhooks (events sent to firm callback URLs).
"""

import hashlib
import hmac
import time
from typing import Any


# Maximum allowed age of a webhook timestamp (5 minutes)
MAX_TIMESTAMP_AGE_SECONDS = 300


def generate_signature(
    payload: bytes,
    secret: str,
    timestamp: int | None = None,
) -> tuple[str, int]:
    """
    Generate an HMAC-SHA256 signature for a webhook payload.

    Returns (signature_hex, timestamp).
    """
    ts = timestamp or int(time.time())
    # Sign the timestamp + payload to prevent replay attacks
    message = f"{ts}.".encode() + payload
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return signature, ts


def verify_signature(
    payload: bytes,
    secret: str,
    signature: str,
    timestamp: int,
    max_age_seconds: int = MAX_TIMESTAMP_AGE_SECONDS,
) -> bool:
    """
    Verify an HMAC-SHA256 webhook signature.

    Checks:
    1. Timestamp is within acceptable window (prevents replay attacks)
    2. Signature matches (constant-time comparison)
    """
    # Check timestamp freshness
    now = int(time.time())
    if abs(now - timestamp) > max_age_seconds:
        return False

    # Recompute and compare
    expected, _ = generate_signature(payload, secret, timestamp)
    return hmac.compare_digest(signature, expected)


def generate_webhook_headers(
    payload: bytes,
    secret: str,
) -> dict[str, str]:
    """
    Generate standard webhook headers for outbound events.

    Returns headers dict with signature and timestamp.
    """
    signature, timestamp = generate_signature(payload, secret)
    return {
        "X-NeuraProp-Signature": signature,
        "X-NeuraProp-Timestamp": str(timestamp),
        "Content-Type": "application/json",
    }


def verify_webhook_request(
    payload: bytes,
    secret: str,
    headers: dict[str, str],
) -> bool:
    """
    Verify inbound webhook using standard NeuraProp headers.

    Expects:
    - X-NeuraProp-Signature: hex-encoded HMAC-SHA256
    - X-NeuraProp-Timestamp: Unix timestamp string
    """
    signature = headers.get("X-NeuraProp-Signature", "")
    timestamp_str = headers.get("X-NeuraProp-Timestamp", "")

    if not signature or not timestamp_str:
        return False

    try:
        timestamp = int(timestamp_str)
    except ValueError:
        return False

    return verify_signature(payload, secret, signature, timestamp)
