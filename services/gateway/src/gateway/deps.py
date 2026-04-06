"""FastAPI dependency injection."""

from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.database import get_db_session
from neuraprop_core.errors import AuthenticationError, TenantNotFoundError


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


FirmId = Annotated[str, Depends(get_firm_id)]
DB = Annotated[AsyncSession, Depends(get_db)]
