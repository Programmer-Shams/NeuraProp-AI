"""Inbound webhook endpoint with signature verification.

Receives events from external services (Veriff KYC callbacks, payment
providers, etc.) and routes them to the appropriate handler.
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from neuraprop_core.logging import get_logger
from neuraprop_core.webhooks import verify_webhook_request
from neuraprop_core.redis import cache_get
from neuraprop_core.sqs import publish_message
from neuraprop_core.config import get_settings

logger = get_logger(__name__)
router = APIRouter()


class WebhookResponse(BaseModel):
    status: str = "received"


@router.post("/webhooks/{provider}", response_model=WebhookResponse)
async def receive_webhook(provider: str, request: Request) -> WebhookResponse:
    """
    Receive and verify an inbound webhook from an external provider.

    Supports: veriff, custom
    Webhook secret is looked up per-firm from Redis/config.
    """
    body = await request.body()
    firm_id = getattr(request.state, "firm_id", None)

    if not firm_id:
        # For provider-specific webhooks, the firm_id may be in the payload or URL
        raise HTTPException(status_code=401, detail="Firm context required for webhooks")

    # Look up the webhook secret for this firm + provider
    secret_key = f"webhook_secret:{firm_id}:{provider}"
    secret_data = await cache_get(secret_key)

    if not secret_data or "secret" not in secret_data:
        logger.warning("webhook_secret_missing", firm_id=firm_id, provider=provider)
        raise HTTPException(status_code=404, detail=f"No webhook configured for provider: {provider}")

    # Verify signature
    headers = dict(request.headers)
    is_valid = verify_webhook_request(
        payload=body,
        secret=secret_data["secret"],
        headers=headers,
    )

    if not is_valid:
        logger.warning(
            "webhook_signature_invalid",
            firm_id=firm_id,
            provider=provider,
        )
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Publish to SQS for async processing
    settings = get_settings()
    await publish_message(
        queue_url=settings.sqs_inbound_queue_url,
        message={
            "type": "webhook",
            "provider": provider,
            "firm_id": firm_id,
            "payload": body.decode("utf-8"),
        },
        message_group_id=f"webhook:{firm_id}:{provider}",
    )

    logger.info("webhook_received", firm_id=firm_id, provider=provider)
    return WebhookResponse(status="received")
