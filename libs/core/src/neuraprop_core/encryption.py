"""Field-level encryption for sensitive data at rest.

Uses AES-256-GCM via the Fernet-compatible approach with the cryptography library.
For use with PII fields, API credentials, and other sensitive values stored in the database.
"""

import base64
import os
from functools import lru_cache

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Nonce size for AES-GCM (96 bits recommended by NIST)
NONCE_SIZE = 12

# Tag is automatically appended by AESGCM (128 bits)


@lru_cache
def _get_encryption_key() -> bytes:
    """
    Load the 256-bit encryption key from environment.

    Key should be a 32-byte value, base64-encoded in the env var.
    Generate with: python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"
    """
    from neuraprop_core.config import get_settings

    settings = get_settings()
    key_b64 = getattr(settings, "encryption_key", "") or os.environ.get("ENCRYPTION_KEY", "")
    if not key_b64:
        # In development, use a deterministic key (NOT safe for production)
        return b"\x00" * 32
    return base64.b64decode(key_b64)


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a string value using AES-256-GCM.

    Returns base64-encoded ciphertext (nonce || ciphertext || tag).
    """
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # Combine nonce + ciphertext for storage
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt_value(encrypted: str) -> str:
    """
    Decrypt a value encrypted with encrypt_value().

    Expects base64-encoded (nonce || ciphertext || tag).
    """
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    raw = base64.b64decode(encrypted)
    nonce = raw[:NONCE_SIZE]
    ciphertext = raw[NONCE_SIZE:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
