"""Normalized data schemas for cross-platform compatibility."""

from integrations.schemas.trading import (
    Platform, TradingAccount, Position, Trade,
    AccountCredentials, AccountResetResult,
    AccountStatus, OrderSide, OrderType, OrderStatus,
)
from integrations.schemas.kyc import (
    VerificationSession, VerificationResult,
    VerificationStatus, DocumentType,
)

__all__ = [
    "Platform", "TradingAccount", "Position", "Trade",
    "AccountCredentials", "AccountResetResult",
    "AccountStatus", "OrderSide", "OrderType", "OrderStatus",
    "VerificationSession", "VerificationResult",
    "VerificationStatus", "DocumentType",
]
