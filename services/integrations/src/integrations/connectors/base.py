"""Base connector interface — all platform connectors implement this contract."""

from abc import ABC, abstractmethod
from typing import Any

from neuraprop_core.logging import get_logger

from integrations.schemas.trading import (
    TradingAccount,
    Position,
    Trade,
    AccountCredentials,
    AccountResetResult,
    Platform,
)

logger = get_logger(__name__)


class BaseConnector(ABC):
    """Abstract base class for all trading platform connectors.

    Every connector must implement the core operations that agents need:
    - Account info (balance, equity, status)
    - Position/trade data
    - Account management (create, reset)

    Connectors normalize platform-specific data into our unified schemas.
    """

    platform: Platform
    name: str
    description: str

    def __init__(self, credentials: dict[str, Any]):
        """Initialize with platform-specific credentials.

        Credentials are loaded from AWS Secrets Manager per firm.
        """
        self.credentials = credentials
        self._initialized = False

    async def initialize(self) -> None:
        """Optional async initialization (connect, authenticate, etc.)."""
        self._initialized = True

    async def close(self) -> None:
        """Cleanup resources."""
        self._initialized = False

    async def health_check(self) -> dict[str, Any]:
        """Check connector health / platform availability."""
        return {"platform": self.platform.value, "status": "ok"}

    # --- Account Operations ---

    @abstractmethod
    async def get_account(self, login: str) -> TradingAccount:
        """Get account details including balance and equity."""
        ...

    @abstractmethod
    async def get_accounts(self, logins: list[str] | None = None) -> list[TradingAccount]:
        """Get multiple accounts. If logins is None, return all managed accounts."""
        ...

    @abstractmethod
    async def create_account(
        self,
        name: str,
        balance: float,
        leverage: int = 100,
        currency: str = "USD",
        group: str | None = None,
    ) -> AccountCredentials:
        """Create a new trading account on the platform."""
        ...

    @abstractmethod
    async def reset_account(self, login: str, new_balance: float) -> AccountResetResult:
        """Reset account balance and clear trade history (challenge restart)."""
        ...

    # --- Trade Data ---

    @abstractmethod
    async def get_open_positions(self, login: str) -> list[Position]:
        """Get all open positions for an account."""
        ...

    @abstractmethod
    async def get_trade_history(
        self, login: str, limit: int = 50, offset: int = 0
    ) -> list[Trade]:
        """Get closed trade history."""
        ...

    # --- Platform Status ---

    @abstractmethod
    async def get_platform_status(self) -> dict[str, Any]:
        """Check if the trading platform is operational."""
        ...


class ConnectorRegistry:
    """Registry of available platform connectors per firm."""

    def __init__(self):
        self._connectors: dict[str, dict[str, BaseConnector]] = {}
        # firm_id -> {platform_name -> connector}

    def register(self, firm_id: str, connector: BaseConnector) -> None:
        if firm_id not in self._connectors:
            self._connectors[firm_id] = {}
        self._connectors[firm_id][connector.platform.value] = connector
        logger.info(
            "connector_registered",
            firm_id=firm_id,
            platform=connector.platform.value,
        )

    def get(self, firm_id: str, platform: str) -> BaseConnector | None:
        return self._connectors.get(firm_id, {}).get(platform)

    def get_for_firm(self, firm_id: str) -> dict[str, BaseConnector]:
        return self._connectors.get(firm_id, {})

    def list_platforms(self, firm_id: str) -> list[str]:
        return list(self._connectors.get(firm_id, {}).keys())


_registry: ConnectorRegistry | None = None


def get_connector_registry() -> ConnectorRegistry:
    global _registry
    if _registry is None:
        _registry = ConnectorRegistry()
    return _registry
