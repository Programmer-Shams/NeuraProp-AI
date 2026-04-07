"""Normalized KYC/verification schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    DECLINED = "declined"
    EXPIRED = "expired"
    RESUBMISSION_REQUIRED = "resubmission_required"


class DocumentType(str, Enum):
    PASSPORT = "passport"
    ID_CARD = "id_card"
    DRIVERS_LICENSE = "drivers_license"
    PROOF_OF_ADDRESS = "proof_of_address"
    SELFIE = "selfie"


class VerificationSession(BaseModel):
    """Normalized KYC verification session."""
    session_id: str
    provider: str  # "veriff", "sumsub", etc.
    status: VerificationStatus = VerificationStatus.PENDING
    verification_url: str | None = None
    document_types_required: list[DocumentType] = Field(default_factory=list)
    created_at: datetime | None = None
    expires_at: datetime | None = None
    decision_at: datetime | None = None
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    """Result of a completed verification."""
    session_id: str
    status: VerificationStatus
    person_name: str | None = None
    document_country: str | None = None
    document_type: DocumentType | None = None
    reason: str | None = None
    risk_score: float | None = None
