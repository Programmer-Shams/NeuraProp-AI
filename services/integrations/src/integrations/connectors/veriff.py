"""Veriff KYC verification connector."""

import hashlib
import hmac
import json
from datetime import datetime, UTC
from typing import Any

import httpx

from neuraprop_core.logging import get_logger

from integrations.schemas.kyc import (
    VerificationSession, VerificationResult, VerificationStatus, DocumentType,
)

logger = get_logger(__name__)

VERIFF_API_URL = "https://stationapi.veriff.com/v1"


class VeriffConnector:
    """Connector for Veriff identity verification.

    Veriff provides KYC/AML identity verification via:
    1. Create a verification session → get a URL
    2. User completes verification at the URL
    3. Receive webhook with results, or poll for status

    Credentials dict expects:
    - api_key: Veriff API key
    - api_secret: Veriff shared secret (for webhook signature verification)
    """

    name = "Veriff"
    description = "Veriff KYC identity verification connector"

    def __init__(self, credentials: dict[str, Any]):
        self.api_key = credentials.get("api_key", "")
        self.api_secret = credentials.get("api_secret", "")
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=VERIFF_API_URL,
            headers={
                "X-AUTH-CLIENT": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )
        logger.info("veriff_connector_initialized")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            raise RuntimeError("Veriff connector not initialized")
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def create_session(
        self,
        first_name: str,
        last_name: str,
        document_type: str = "PASSPORT",
        callback_url: str | None = None,
        vendor_data: str | None = None,
    ) -> VerificationSession:
        """Create a new Veriff verification session.

        Returns a session with a URL the user should visit to complete verification.
        """
        payload: dict[str, Any] = {
            "verification": {
                "person": {
                    "firstName": first_name,
                    "lastName": last_name,
                },
                "document": {
                    "type": document_type,
                },
                "vendorData": vendor_data or "",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        if callback_url:
            payload["verification"]["callback"] = callback_url

        data = await self._request("POST", "/sessions", json=payload)
        verification = data.get("verification", {})

        return VerificationSession(
            session_id=verification.get("id", ""),
            provider="veriff",
            status=VerificationStatus.PENDING,
            verification_url=verification.get("url"),
            created_at=datetime.now(UTC),
            metadata={"vendor_data": vendor_data},
        )

    async def get_session_status(self, session_id: str) -> VerificationResult:
        """Get the decision/status for a verification session."""
        data = await self._request("GET", f"/sessions/{session_id}/decision")
        verification = data.get("verification", {})
        status_map = {
            "approved": VerificationStatus.APPROVED,
            "declined": VerificationStatus.DECLINED,
            "resubmission_requested": VerificationStatus.RESUBMISSION_REQUIRED,
            "expired": VerificationStatus.EXPIRED,
            "created": VerificationStatus.PENDING,
            "started": VerificationStatus.IN_PROGRESS,
        }

        person = verification.get("person", {})
        document = verification.get("document", {})

        return VerificationResult(
            session_id=session_id,
            status=status_map.get(verification.get("status", ""), VerificationStatus.PENDING),
            person_name=f"{person.get('firstName', '')} {person.get('lastName', '')}".strip() or None,
            document_country=document.get("country"),
            reason=verification.get("reasonCode"),
        )

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify the HMAC signature on a Veriff webhook callback."""
        expected = hmac.new(
            self.api_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook(self, data: dict) -> VerificationResult:
        """Parse a Veriff webhook notification into a VerificationResult."""
        verification = data.get("verification", {})
        person = verification.get("person", {})

        status_map = {
            "approved": VerificationStatus.APPROVED,
            "declined": VerificationStatus.DECLINED,
            "resubmission_requested": VerificationStatus.RESUBMISSION_REQUIRED,
            "expired": VerificationStatus.EXPIRED,
        }

        return VerificationResult(
            session_id=verification.get("id", ""),
            status=status_map.get(verification.get("status", ""), VerificationStatus.PENDING),
            person_name=f"{person.get('firstName', '')} {person.get('lastName', '')}".strip() or None,
            document_country=verification.get("document", {}).get("country"),
            reason=verification.get("reasonCode"),
            risk_score=verification.get("riskScore"),
        )
