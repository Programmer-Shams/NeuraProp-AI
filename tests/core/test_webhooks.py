"""Tests for neuraprop_core.webhooks — HMAC signature generation and verification."""

import time

import pytest

from neuraprop_core.webhooks import (
    generate_signature,
    verify_signature,
    generate_webhook_headers,
    verify_webhook_request,
    MAX_TIMESTAMP_AGE_SECONDS,
)


class TestGenerateSignature:
    def test_returns_hex_string_and_timestamp(self):
        sig, ts = generate_signature(b"payload", "secret")
        assert isinstance(sig, str)
        assert len(sig) == 64  # SHA-256 hex
        assert isinstance(ts, int)

    def test_deterministic_with_same_timestamp(self):
        ts = int(time.time())
        sig1, _ = generate_signature(b"payload", "secret", timestamp=ts)
        sig2, _ = generate_signature(b"payload", "secret", timestamp=ts)
        assert sig1 == sig2

    def test_different_secrets_produce_different_signatures(self):
        ts = int(time.time())
        sig1, _ = generate_signature(b"payload", "secret1", timestamp=ts)
        sig2, _ = generate_signature(b"payload", "secret2", timestamp=ts)
        assert sig1 != sig2

    def test_different_payloads_produce_different_signatures(self):
        ts = int(time.time())
        sig1, _ = generate_signature(b"payload1", "secret", timestamp=ts)
        sig2, _ = generate_signature(b"payload2", "secret", timestamp=ts)
        assert sig1 != sig2


class TestVerifySignature:
    def test_valid_signature(self):
        sig, ts = generate_signature(b"test payload", "my_secret")
        assert verify_signature(b"test payload", "my_secret", sig, ts) is True

    def test_wrong_payload(self):
        sig, ts = generate_signature(b"test payload", "my_secret")
        assert verify_signature(b"wrong payload", "my_secret", sig, ts) is False

    def test_wrong_secret(self):
        sig, ts = generate_signature(b"test payload", "my_secret")
        assert verify_signature(b"test payload", "wrong_secret", sig, ts) is False

    def test_expired_timestamp(self):
        old_ts = int(time.time()) - MAX_TIMESTAMP_AGE_SECONDS - 10
        sig, _ = generate_signature(b"test", "secret", timestamp=old_ts)
        assert verify_signature(b"test", "secret", sig, old_ts) is False

    def test_future_timestamp_within_window(self):
        future_ts = int(time.time()) + 60  # 1 minute in future
        sig, _ = generate_signature(b"test", "secret", timestamp=future_ts)
        assert verify_signature(b"test", "secret", sig, future_ts) is True

    def test_future_timestamp_beyond_window(self):
        far_future = int(time.time()) + MAX_TIMESTAMP_AGE_SECONDS + 100
        sig, _ = generate_signature(b"test", "secret", timestamp=far_future)
        assert verify_signature(b"test", "secret", sig, far_future) is False


class TestWebhookHeaders:
    def test_generates_required_headers(self):
        headers = generate_webhook_headers(b'{"event": "test"}', "secret")
        assert "X-NeuraProp-Signature" in headers
        assert "X-NeuraProp-Timestamp" in headers
        assert headers["Content-Type"] == "application/json"

    def test_headers_are_verifiable(self):
        payload = b'{"event": "kyc.completed"}'
        secret = "webhook_secret_123"
        headers = generate_webhook_headers(payload, secret)
        assert verify_webhook_request(payload, secret, headers) is True


class TestVerifyWebhookRequest:
    def test_valid_request(self):
        payload = b'{"data": "test"}'
        secret = "secret123"
        headers = generate_webhook_headers(payload, secret)
        assert verify_webhook_request(payload, secret, headers) is True

    def test_missing_signature_header(self):
        assert verify_webhook_request(b"test", "secret", {"X-NeuraProp-Timestamp": "123"}) is False

    def test_missing_timestamp_header(self):
        assert verify_webhook_request(b"test", "secret", {"X-NeuraProp-Signature": "abc"}) is False

    def test_invalid_timestamp(self):
        headers = {
            "X-NeuraProp-Signature": "abc123",
            "X-NeuraProp-Timestamp": "not-a-number",
        }
        assert verify_webhook_request(b"test", "secret", headers) is False

    def test_tampered_payload(self):
        payload = b'{"data": "original"}'
        secret = "secret123"
        headers = generate_webhook_headers(payload, secret)
        assert verify_webhook_request(b'{"data": "tampered"}', secret, headers) is False
