"""FastAPI dependency injection."""

from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.auth import verify_jwt_token
from neuraprop_core.database import get_db_session
from neuraprop_core.errors import AuthenticationError, AuthorizationError, TenantNotFoundError


async def get_firm_id(request: Request) -> str:
    """Extract firm_id from request state (set by TenantMiddleware)."""
    firm_id = getattr(request.state, "firm_id", None)
    if not firm_id:
        raise TenantNotFoundError("No firm context. Provide X-API-Key header.")
    return firm_id


async def get_db(request: Request) -> AsyncSession:
    """Get a tenant-scoped database session."""
    firm_id = await get_firm_id(request)
    async with get_db_session(firm_id=firm_id) as session:
        yield session


async def get_jwt_claims(request: Request) -> dict:
    """
    Verify JWT Bearer token from the Authorization header.

    Used for dashboard routes where Clerk provides the JWT.
    Returns decoded claims containing sub, firm_id, role.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthenticationError("Authorization header with Bearer token required")

    token = auth_header[7:]
    claims = verify_jwt_token(token)

    # Bind claims to request state for downstream use
    request.state.user_id = claims.get("sub")
    request.state.user_role = claims.get("role", "viewer")
    request.state.jwt_firm_id = claims.get("firm_id")

    return claims


async def require_role(request: Request, required_role: str = "admin") -> dict:
    """Verify JWT and check that user has the required role."""
    claims = await get_jwt_claims(request)
    user_role = claims.get("role", "viewer")

    role_hierarchy = {"viewer": 0, "agent": 1, "admin": 2, "owner": 3}
    if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 99):
        raise AuthorizationError(
            f"Role '{required_role}' required, you have '{user_role}'"
        )
    return claims


async def require_admin(request: Request) -> dict:
    """Shortcut: verify JWT and require admin role."""
    return await require_role(request, "admin")


async def require_owner(request: Request) -> dict:
    """Shortcut: verify JWT and require owner role."""
    return await require_role(request, "owner")


FirmId = Annotated[str, Depends(get_firm_id)]
DB = Annotated[AsyncSession, Depends(get_db)]
JWTClaims = Annotated[dict, Depends(get_jwt_claims)]
AdminClaims = Annotated[dict, Depends(require_admin)]
OwnerClaims = Annotated[dict, Depends(require_owner)]
