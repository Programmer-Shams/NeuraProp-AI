"""Email parser — extracts structured data from inbound emails (SES notifications)."""

import email
import re
from dataclasses import dataclass, field
from email.utils import parseaddr
from typing import Any


@dataclass
class ParsedEmail:
    """Structured representation of an inbound email."""

    message_id: str
    from_address: str
    from_name: str
    to_address: str
    subject: str
    body_text: str
    body_html: str
    in_reply_to: str | None = None
    references: list[str] = field(default_factory=list)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def is_reply(self) -> bool:
        """Check if this email is a reply to a previous thread."""
        return bool(self.in_reply_to or self.references)

    @property
    def thread_id(self) -> str | None:
        """Extract thread ID from references or in-reply-to headers."""
        if self.references:
            return self.references[0]
        return self.in_reply_to


def parse_ses_notification(ses_event: dict) -> ParsedEmail:
    """
    Parse an SES inbound email notification.

    SES delivers the raw MIME content in the notification or stores it in S3.
    """
    mail = ses_event.get("mail", {})
    receipt = ses_event.get("receipt", {})

    headers = {h["name"]: h["value"] for h in mail.get("headers", [])}

    from_name, from_address = parseaddr(headers.get("From", ""))
    to_address = headers.get("To", "")
    subject = headers.get("Subject", "")

    return ParsedEmail(
        message_id=mail.get("messageId", ""),
        from_address=from_address,
        from_name=from_name or from_address.split("@")[0],
        to_address=to_address,
        subject=subject,
        body_text="",  # Filled by parse_mime_content
        body_html="",
        in_reply_to=headers.get("In-Reply-To"),
        references=headers.get("References", "").split() if headers.get("References") else [],
        headers=headers,
    )


def parse_mime_content(raw_email: str) -> ParsedEmail:
    """Parse raw MIME email content into structured format."""
    msg = email.message_from_string(raw_email)

    from_name, from_address = parseaddr(msg.get("From", ""))
    to_address = msg.get("To", "")
    subject = msg.get("Subject", "")
    message_id = msg.get("Message-ID", "")
    in_reply_to = msg.get("In-Reply-To")
    references = msg.get("References", "").split() if msg.get("References") else []

    body_text = ""
    body_html = ""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                attachments.append({
                    "filename": part.get_filename() or "unnamed",
                    "content_type": content_type,
                    "size": len(part.get_payload(decode=True) or b""),
                })
            elif content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body_text = payload.decode("utf-8", errors="replace")
            elif content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    body_html = payload.decode("utf-8", errors="replace")
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            decoded = payload.decode("utf-8", errors="replace")
            if content_type == "text/html":
                body_html = decoded
            else:
                body_text = decoded

    # Clean the body — strip quoted replies for cleaner agent context
    body_text = _strip_quoted_reply(body_text)

    return ParsedEmail(
        message_id=message_id,
        from_address=from_address,
        from_name=from_name or from_address.split("@")[0],
        to_address=to_address,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        in_reply_to=in_reply_to,
        references=references,
        attachments=attachments,
    )


def _strip_quoted_reply(text: str) -> str:
    """Strip quoted reply text from email body to get only the new message."""
    if not text:
        return ""

    # Common reply markers
    markers = [
        r"^On .+ wrote:$",
        r"^-{3,}\s*Original Message\s*-{3,}$",
        r"^>{1,}\s",
        r"^From:\s",
        r"^Sent:\s",
    ]

    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        if any(re.match(pattern, line.strip(), re.IGNORECASE) for pattern in markers):
            break
        clean_lines.append(line)

    return "\n".join(clean_lines).strip()
