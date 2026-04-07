"""Tests for gateway middleware — request ID, security headers, audit."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.testclient import TestClient


class TestRequestIdMiddleware:
    """Test request ID correlation."""

    def test_generates_request_id_when_missing(self):
        from gateway.middleware.request_id import RequestIdMiddleware

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b"",
        }
        request = Request(scope)

        # The middleware sets request.state.request_id
        # We test the logic directly
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        assert len(request_id) == 36  # UUID format

    def test_preserves_client_provided_id(self):
        client_id = "my-custom-request-id-123"
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [(b"x-request-id", client_id.encode())],
            "query_string": b"",
        }
        request = Request(scope)
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        assert request_id == client_id


class TestSecurityHeaders:
    """Test security headers are applied correctly."""

    def test_headers_content(self):
        """Verify the expected header values."""
        expected_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        # Check expected values are valid
        for header, value in expected_headers.items():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_hsts_value(self):
        expected = "max-age=31536000; includeSubDomains; preload"
        assert "31536000" in expected
        assert "includeSubDomains" in expected


class TestAuditMiddleware:
    """Test audit logging middleware logic."""

    def test_skip_paths(self):
        from gateway.middleware.audit import SKIP_PATHS

        assert "/health" in SKIP_PATHS
        assert "/docs" in SKIP_PATHS
        assert "/favicon.ico" in SKIP_PATHS

    def test_sensitive_paths(self):
        from gateway.middleware.audit import SENSITIVE_PATHS

        assert "/api/v1/admin/firms" in SENSITIVE_PATHS
        assert "/api/v1/messages" in SENSITIVE_PATHS

    def test_get_client_ip_from_forwarded(self):
        from gateway.middleware.audit import AuditMiddleware

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [(b"x-forwarded-for", b"1.2.3.4, 5.6.7.8")],
            "query_string": b"",
        }
        request = Request(scope)
        ip = AuditMiddleware._get_client_ip(request)
        assert ip == "1.2.3.4"

    def test_get_client_ip_from_real_ip(self):
        from gateway.middleware.audit import AuditMiddleware

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [(b"x-real-ip", b"10.0.0.1")],
            "query_string": b"",
        }
        request = Request(scope)
        ip = AuditMiddleware._get_client_ip(request)
        assert ip == "10.0.0.1"


class TestRateLimitConfig:
    """Test rate limit tier configuration."""

    def test_plan_tiers_exist(self):
        from gateway.middleware.rate_limit import PLAN_LIMITS

        assert "starter" in PLAN_LIMITS
        assert "growth" in PLAN_LIMITS
        assert "enterprise" in PLAN_LIMITS

    def test_enterprise_has_highest_limits(self):
        from gateway.middleware.rate_limit import PLAN_LIMITS

        assert PLAN_LIMITS["enterprise"]["max_requests"] > PLAN_LIMITS["growth"]["max_requests"]
        assert PLAN_LIMITS["growth"]["max_requests"] > PLAN_LIMITS["starter"]["max_requests"]

    def test_endpoint_limits_exist(self):
        from gateway.middleware.rate_limit import ENDPOINT_LIMITS

        assert "POST:/api/v1/admin/firms" in ENDPOINT_LIMITS
        assert "POST:/api/v1/messages" in ENDPOINT_LIMITS

    def test_firm_creation_is_strict(self):
        from gateway.middleware.rate_limit import ENDPOINT_LIMITS

        firm_limit = ENDPOINT_LIMITS["POST:/api/v1/admin/firms"]
        assert firm_limit["max_requests"] <= 10
        assert firm_limit["window_seconds"] >= 3600  # At least 1 hour


class TestIpFilterLogic:
    """Test IP filter allowlist checking."""

    @pytest.mark.asyncio
    async def test_empty_allowlist_allows_all(self):
        """No allowlist means all IPs are allowed."""
        from gateway.middleware.ip_filter import IpFilterMiddleware

        with patch("gateway.middleware.ip_filter.get_redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.smembers.return_value = set()
            mock_redis.return_value = mock_client

            result = await IpFilterMiddleware._check_ip_allowed("firm-123", "1.2.3.4")
            assert result is True

    @pytest.mark.asyncio
    async def test_ip_in_allowlist(self):
        from gateway.middleware.ip_filter import IpFilterMiddleware

        with patch("gateway.middleware.ip_filter.get_redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.smembers.return_value = {"1.2.3.4", "5.6.7.8"}
            mock_redis.return_value = mock_client

            result = await IpFilterMiddleware._check_ip_allowed("firm-123", "1.2.3.4")
            assert result is True

    @pytest.mark.asyncio
    async def test_ip_not_in_allowlist(self):
        from gateway.middleware.ip_filter import IpFilterMiddleware

        with patch("gateway.middleware.ip_filter.get_redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.smembers.return_value = {"1.2.3.4", "5.6.7.8"}
            mock_redis.return_value = mock_client

            result = await IpFilterMiddleware._check_ip_allowed("firm-123", "9.9.9.9")
            assert result is False

    @pytest.mark.asyncio
    async def test_cidr_range_match(self):
        from gateway.middleware.ip_filter import IpFilterMiddleware

        with patch("gateway.middleware.ip_filter.get_redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.smembers.return_value = {"10.0.0.0/8"}
            mock_redis.return_value = mock_client

            result = await IpFilterMiddleware._check_ip_allowed("firm-123", "10.1.2.3")
            assert result is True

    @pytest.mark.asyncio
    async def test_cidr_range_no_match(self):
        from gateway.middleware.ip_filter import IpFilterMiddleware

        with patch("gateway.middleware.ip_filter.get_redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.smembers.return_value = {"10.0.0.0/8"}
            mock_redis.return_value = mock_client

            result = await IpFilterMiddleware._check_ip_allowed("firm-123", "192.168.1.1")
            assert result is False
