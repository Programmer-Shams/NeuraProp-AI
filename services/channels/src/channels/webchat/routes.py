"""WebSocket routes for the web chat widget — mounted in the FastAPI gateway."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from neuraprop_core.logging import get_logger

from channels.webchat.adapter import handle_websocket, get_active_session_count

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["webchat"])


@router.websocket("/chat")
async def websocket_chat(
    websocket: WebSocket,
    firm_id: str = Query(..., description="Firm ID for tenant routing"),
):
    """
    WebSocket endpoint for the embeddable chat widget.

    Connect with: ws://host/ws/chat?firm_id=<firm_id>

    The widget authenticates via firm_id (public, embedded in widget script).
    Trader identity is optional and resolved server-side.
    """
    await websocket.accept()

    logger.info("websocket_accepted", firm_id=firm_id)

    try:
        await handle_websocket(websocket, firm_id)
    except WebSocketDisconnect:
        logger.info("websocket_disconnected", firm_id=firm_id)
    except Exception:
        logger.exception("websocket_error", firm_id=firm_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass


@router.get("/chat/health")
async def webchat_health():
    """Health check for the web chat service."""
    return {
        "status": "ok",
        "active_sessions": get_active_session_count(),
    }
