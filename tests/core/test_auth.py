"""Tests for neuraprop_core.auth — API key and JWT utilities."""

import os
import time

import pytest

# Ensure test secret is set before import
os.environ["CLERK_SECRET_KEY"] = "test-secret-key-for-jwt-signing-32chars"

from neuraprop_core.auth import (
    generate_api_key,
    hash_api_key,
    extract_firm_slug,
    create_jwt_token,
    verify_jwt_token,
)
from neuraprop_core.errors import AuthenticationError


class TestGenerateApiKey:
    def test_format(self):
        key = generate_api_key("testfirm", "live")
        assert key.startswith("np_live_testfirm_")

    def test_test_environment(self):
        key = generate_api_key("myfirm", "test")
        assert key.startswith("np_test_myfirm_")

    def test_uniqueness(self):
        keys = {generate_api_key("firm", "live") for _ in range(100)}
        assert len(keys) == 100  # All unique

    def test_sufficient_entropy(self):
        key = generate_api_key("firm", "live")
        random_part = key.split("_", 3)[3]
        assert len(random_part) >= 20


class TestHashApiKey:
    def test_returns_hex_string(self):
        h = hash_api_key("np_live_test_abc")
        assert len(h) == 64  # SHA-256 hex

    def test_deterministic(self):
        key = "np_live_test_abc123"
        assert hash_api_key(key) == hash_api_key(key)

    def test_different_keys_different_hashes(self):
        assert hash_api_key("key1") != hash_api_key("key2")


class TestExtractFirmSlug:
    def test_extracts_slug(self):
        slug = extract_firm_slug("np_live_alphacap_random123")
        assert slug == "alphacap"

    def test_extracts_from_test_key(self):
        slug = extract_firm_slug("np_test_myfirm_random456")
        assert slug == "myfirm"

    def test_returns_none_for_invalid_format(self):
        assert extract_firm_slug("invalid_key") is None

    def test_returns_none_for_wrong_prefix(self):
        assert extract_firm_slug("sk_live_firm_abc") is None


class TestJwtToken:
    def test_create_and_verify(self):
        token = create_jwt_token(
            subject="user_123",
            firm_id="firm_456",
            role="admin",
        )
        claims = verify_jwt_token(token)
        assert claims["sub"] == "user_123"
        assert claims["firm_id"] == "firm_456"
        assert claims["role"] == "admin"

    def test_extra_claims(self):
        token = create_jwt_token(
            subject="user_1",
            firm_id="firm_1",
            extra_claims={"team": "support"},
        )
        claims = verify_jwt_token(token)
        assert claims["team"] == "support"

    def test_expired_token_raises(self):
        from datetime import UTC, datetime, timedelta
        from jose import jwt as jose_jwt

        settings_key = "test-secret-key-for-jwt-signing-32chars"
        expired = {
            "sub": "user",
            "firm_id": "firm",
            "role": "admin",
            "iat": datetime.now(UTC) - timedelta(hours=1),
            "exp": datetime.now(UTC) - timedelta(minutes=30),
        }
        token = jose_jwt.encode(expired, settings_key, algorithm="HS256")
        with pytest.raises(AuthenticationError, match="expired"):
            verify_jwt_token(token)

    def test_invalid_token_raises(self):
        with pytest.raises(AuthenticationError, match="Invalid"):
            verify_jwt_token("not.a.valid.token")

    def test_tampered_token_raises(self):
        token = create_jwt_token("user", "firm")
        # Flip a character
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(AuthenticationError):
            verify_jwt_token(tampered)
