"""Email sender — sends outbound emails via SendGrid with proper threading headers."""

from typing import Any

import httpx

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger

logger = get_logger(__name__)

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


async def send_email(
    to_address: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
    from_address: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
    in_reply_to: str | None = None,
    references: list[str] | None = None,
    firm_id: str | None = None,
) -> dict[str, Any]:
    """
    Send an email via SendGrid.

    Supports email threading via In-Reply-To and References headers
    for proper thread grouping in email clients.
    """
    settings = get_settings()

    if not settings.sendgrid_api_key:
        logger.warning("sendgrid_not_configured")
        return {"success": False, "error": "SendGrid not configured"}

    # Default from address: support@{firm_slug}.neuraprop.ai
    if not from_address:
        from_address = "support@neuraprop.ai"
    if not from_name:
        from_name = "NeuraProp Support"

    payload: dict[str, Any] = {
        "personalizations": [{"to": [{"email": to_address}]}],
        "from": {"email": from_address, "name": from_name},
        "subject": subject,
        "content": [],
    }

    # Add text content
    payload["content"].append({"type": "text/plain", "value": body_text})

    # Add HTML content if provided
    if body_html:
        payload["content"].append({"type": "text/html", "value": body_html})

    # Reply-To header
    if reply_to:
        payload["reply_to"] = {"email": reply_to}

    # Threading headers for email clients
    headers = {}
    if in_reply_to:
        headers["In-Reply-To"] = in_reply_to
    if references:
        headers["References"] = " ".join(references)
    if headers:
        payload["headers"] = headers

    # Custom tracking category
    payload["categories"] = ["neuraprop_support"]
    if firm_id:
        payload["categories"].append(f"firm_{firm_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SENDGRID_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.sendgrid_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )

        if response.status_code in (200, 201, 202):
            logger.info(
                "email_sent",
                to=to_address,
                subject=subject[:50],
                firm_id=firm_id,
            )
            return {"success": True, "status_code": response.status_code}
        else:
            logger.error(
                "email_send_failed",
                status=response.status_code,
                body=response.text[:200],
            )
            return {"success": False, "error": response.text, "status_code": response.status_code}

    except Exception as e:
        logger.exception("email_send_error")
        return {"success": False, "error": str(e)}


def build_html_response(body_text: str, firm_name: str = "NeuraProp") -> str:
    """Build a clean HTML email template for agent responses."""
    # Escape HTML in body text
    escaped = body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Convert newlines to <br>
    html_body = escaped.replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
    <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 20px;">
        <strong style="font-size: 16px; color: #2563eb;">{firm_name} Support</strong>
    </div>
    <div style="line-height: 1.6; font-size: 14px;">
        {html_body}
    </div>
    <div style="margin-top: 30px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af;">
        This is an automated response from {firm_name} Support. Reply to this email to continue the conversation.
    </div>
</body>
</html>"""
