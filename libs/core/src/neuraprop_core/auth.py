"""API key validation and authentication utilities."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from neuraprop_core.config import get_settings
from neuraprop_core.errors import AuthenticationError

# JWT settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 15


def generate_api_key(firm_slug: str, environment: str = "live") -> str:
    """
    Generate a new API key for a firm.

    Format: np_{env}_{slug}_{random}
    """
    random_part = secrets.token_urlsafe(32)
    return f"np_{environment}_{firm_slug}_{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def extract_firm_slug(api_key: str) -> str | None:
    """
    Extract the firm slug from an API key for quick routing.

    API key format: np_{env}_{slug}_{random}
    """
    parts = api_key.split("_", 3)
    if len(parts) >= 3 and parts[0] == "np":
        return parts[2]
    return None


def create_jwt_token(
    subject: str,
    firm_id: str,
    role: str = "admin",
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT token for dashboard authentication."""
    settings = get_settings()
    now = datetime.now(UTC)
    claims = {
        "sub": subject,
        "firm_id": firm_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRY_MINUTES),
    }
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, settings.clerk_secret_key, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.clerk_secret_key,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError as e:
        raise AuthenticationError(f"Invalid token: {e}")
