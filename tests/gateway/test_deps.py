"""Tests for gateway dependency injection — JWT auth and role checks."""

import os
import pytest
from unittest.mock import MagicMock

os.environ["CLERK_SECRET_KEY"] = "test-secret-key-for-jwt-signing-32chars"

from neuraprop_core.auth import create_jwt_token
from neuraprop_core.errors import AuthenticationError, AuthorizationError
from gateway.deps import get_jwt_claims, require_role


class TestGetJwtClaims:
    @pytest.mark.asyncio
    async def test_valid_bearer_token(self):
        token = create_jwt_token("user_1", "firm_1", "admin")
        request = MagicMock()
        request.headers = {"Authorization": f"Bearer {token}"}
        request.state = MagicMock()

        claims = await get_jwt_claims(request)
        assert claims["sub"] == "user_1"
        assert claims["firm_id"] == "firm_1"
        assert claims["role"] == "admin"

    @pytest.mark.asyncio
    async def test_missing_auth_header(self):
        request = MagicMock()
        request.headers = {}

        with pytest.raises(AuthenticationError, match="Bearer"):
            await get_jwt_claims(request)

    @pytest.mark.asyncio
    async def test_wrong_auth_scheme(self):
        request = MagicMock()
        request.headers = {"Authorization": "Basic abc123"}

        with pytest.raises(AuthenticationError, match="Bearer"):
            await get_jwt_claims(request)

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        request = MagicMock()
        request.headers = {"Authorization": "Bearer invalid.token.here"}

        with pytest.raises(AuthenticationError):
            await get_jwt_claims(request)


class TestRequireRole:
    @pytest.mark.asyncio
    async def test_admin_has_admin_access(self):
        token = create_jwt_token("user_1", "firm_1", "admin")
        request = MagicMock()
        request.headers = {"Authorization": f"Bearer {token}"}
        request.state = MagicMock()

        claims = await require_role(request, "admin")
        assert claims["role"] == "admin"

    @pytest.mark.asyncio
    async def test_owner_has_admin_access(self):
        token = create_jwt_token("user_1", "firm_1", "owner")
        request = MagicMock()
        request.headers = {"Authorization": f"Bearer {token}"}
        request.state = MagicMock()

        claims = await require_role(request, "admin")
        assert claims["role"] == "owner"

    @pytest.mark.asyncio
    async def test_viewer_denied_admin_access(self):
        token = create_jwt_token("user_1", "firm_1", "viewer")
        request = MagicMock()
        request.headers = {"Authorization": f"Bearer {token}"}
        request.state = MagicMock()

        with pytest.raises(AuthorizationError, match="admin"):
            await require_role(request, "admin")

    @pytest.mark.asyncio
    async def test_agent_denied_owner_access(self):
        token = create_jwt_token("user_1", "firm_1", "agent")
        request = MagicMock()
        request.headers = {"Authorization": f"Bearer {token}"}
        request.state = MagicMock()

        with pytest.raises(AuthorizationError, match="owner"):
            await require_role(request, "owner")
