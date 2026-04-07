"""Email adapter — handles inbound SES emails and outbound SendGrid responses."""

import uuid
from datetime import UTC, datetime
from typing import Any

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger
from neuraprop_core.sqs import publish_message

from channels.email.parser import ParsedEmail, parse_ses_notification, parse_mime_content
from channels.email.sender import send_email, build_html_response

logger = get_logger(__name__)


def extract_firm_from_email(to_address: str) -> str | None:
    """
    Extract firm ID from the support email address.

    Format: support@{firm_slug}.neuraprop.ai
    Returns the firm_slug portion.
    """
    if "@" not in to_address:
        return None

    domain = to_address.split("@")[1].lower()

    # support@firmslug.neuraprop.ai
    if domain.endswith(".neuraprop.ai"):
        parts = domain.split(".")
        if len(parts) >= 3:
            return parts[0]

    # Fallback: support@neuraprop.ai -> demo firm
    if domain == "neuraprop.ai":
        return "demo"

    return None


async def handle_ses_notification(ses_event: dict) -> dict[str, Any]:
    """
    Handle an inbound email from AWS SES.

    Called by a Lambda function triggered by SES receipt rules.
    Parses the email and publishes to the agent pipeline.
    """
    parsed = parse_ses_notification(ses_event)
    return await _process_inbound_email(parsed)


async def handle_raw_email(raw_mime: str) -> dict[str, Any]:
    """Handle a raw MIME email (for testing or alternative ingestion)."""
    parsed = parse_mime_content(raw_mime)
    return await _process_inbound_email(parsed)


async def _process_inbound_email(parsed: ParsedEmail) -> dict[str, Any]:
    """Process a parsed email into the agent pipeline."""
    settings = get_settings()

    # Resolve firm from the To address
    firm_id = extract_firm_from_email(parsed.to_address)
    if not firm_id:
        logger.warning("email_unknown_firm", to=parsed.to_address)
        return {"success": False, "error": "Unknown firm from email address"}

    message_id = str(uuid.uuid4())

    # Use text body, fall back to stripping HTML
    content = parsed.body_text or parsed.subject or ""
    if not content.strip():
        logger.warning("email_empty_content", from_addr=parsed.from_address)
        return {"success": False, "error": "Empty email content"}

    unified_message = {
        "id": message_id,
        "firm_id": firm_id,
        "channel": "email",
        "direction": "inbound",
        "sender_type": "trader",
        "sender_channel_id": parsed.from_address,
        "sender_display_name": parsed.from_name,
        "trader_id": None,
        "content": content,
        "attachments": parsed.attachments,
        "metadata": {
            "email_message_id": parsed.message_id,
            "email_subject": parsed.subject,
            "email_in_reply_to": parsed.in_reply_to,
            "email_references": parsed.references,
            "email_from": parsed.from_address,
        },
        "conversation_id": None,
        "reply_to_message_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "channel_timestamp": datetime.now(UTC).isoformat(),
    }

    # Use thread_id to link to existing conversation
    if parsed.thread_id:
        unified_message["metadata"]["thread_id"] = parsed.thread_id

    await publish_message(
        queue_url=settings.sqs_inbound_queue_url,
        message=unified_message,
        message_group_id=firm_id,
    )

    logger.info(
        "email_message_queued",
        message_id=message_id,
        firm_id=firm_id,
        from_addr=parsed.from_address,
        is_reply=parsed.is_reply,
    )

    return {"success": True, "message_id": message_id}


async def send_agent_response_email(
    to_address: str,
    agent_response: str,
    firm_id: str,
    firm_name: str = "NeuraProp",
    subject: str = "Re: Your Support Request",
    in_reply_to: str | None = None,
    references: list[str] | None = None,
) -> dict[str, Any]:
    """
    Send an agent response back to the trader via email.

    Maintains email threading so replies appear in the same thread.
    """
    from_address = f"support@{firm_id}.neuraprop.ai"
    html_body = build_html_response(agent_response, firm_name)

    result = await send_email(
        to_address=to_address,
        subject=subject,
        body_text=agent_response,
        body_html=html_body,
        from_address=from_address,
        from_name=f"{firm_name} Support",
        in_reply_to=in_reply_to,
        references=references,
        firm_id=firm_id,
    )

    logger.info(
        "email_response_sent",
        to=to_address,
        firm_id=firm_id,
        success=result.get("success"),
    )

    return result
