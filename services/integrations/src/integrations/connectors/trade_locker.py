"""TradeLocker API connector."""

from datetime import datetime, UTC
from typing import Any

import httpx

from neuraprop_core.logging import get_logger

from integrations.connectors.base import BaseConnector
from integrations.schemas.trading import (
    TradingAccount, Position, Trade, AccountCredentials,
    AccountResetResult, Platform, AccountStatus, OrderSide,
)

logger = get_logger(__name__)


class TradeLockerConnector(BaseConnector):
    """Connector for TradeLocker platform.

    TradeLocker is a newer trading platform popular with prop firms,
    featuring a modern REST API with JWT authentication.

    Credentials dict expects:
    - api_url: TradeLocker API base URL
    - email: API account email
    - password: API account password
    - server: Server identifier
    """

    platform = Platform.TRADE_LOCKER
    name = "TradeLocker"
    description = "TradeLocker API connector for account and trade management"

    def __init__(self, credentials: dict[str, Any]):
        super().__init__(credentials)
        self.api_url = credentials.get("api_url", "https://api.tradelocker.com")
        self._email = credentials.get("email", "")
        self._password = credentials.get("password", "")
        self.server = credentials.get("server", "")
        self._access_token = ""
        self._refresh_token = ""
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            timeout=15.0,
        )
        # Authenticate and get JWT tokens
        await self._authenticate()
        await super().initialize()
        logger.info("trade_locker_connector_initialized", server=self.server)

    async def _authenticate(self) -> None:
        """Authenticate with TradeLocker to get JWT tokens."""
        if not self._client:
            raise RuntimeError("TradeLocker connector not initialized")
        response = await self._client.post("/auth/jwt/token", json={
            "email": self._email,
            "password": self._password,
            "server": self.server,
        })
        response.raise_for_status()
        data = response.json()
        self._access_token = data["accessToken"]
        self._refresh_token = data.get("refreshToken", "")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
        await super().close()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            raise RuntimeError("TradeLocker connector not initialized")
        response = await self._client.request(
            method, path,
            headers={"Authorization": f"Bearer {self._access_token}"},
            **kwargs,
        )
        # Handle token refresh on 401
        if response.status_code == 401 and self._refresh_token:
            await self._refresh_auth()
            response = await self._client.request(
                method, path,
                headers={"Authorization": f"Bearer {self._access_token}"},
                **kwargs,
            )
        response.raise_for_status()
        return response.json()

    async def _refresh_auth(self) -> None:
        if not self._client:
            return
        response = await self._client.post("/auth/jwt/refresh", json={
            "refreshToken": self._refresh_token,
        })
        response.raise_for_status()
        data = response.json()
        self._access_token = data["accessToken"]
        self._refresh_token = data.get("refreshToken", self._refresh_token)

    async def get_account(self, login: str) -> TradingAccount:
        data = await self._request("GET", f"/trade/accounts/{login}")
        acc = data.get("account", data)
        return TradingAccount(
            account_id=f"TL-{login}",
            platform=Platform.TRADE_LOCKER,
            login=login,
            server=self.server,
            name=acc.get("name", ""),
            currency=acc.get("currency", "USD"),
            balance=float(acc.get("balance", 0)),
            equity=float(acc.get("equity", 0)),
            margin=float(acc.get("usedMargin", 0)),
            free_margin=float(acc.get("freeMargin", 0)),
            profit=float(acc.get("unrealizedPnl", 0)),
            leverage=int(acc.get("leverage", 100)),
            status=AccountStatus.ACTIVE if acc.get("isActive") else AccountStatus.SUSPENDED,
        )

    async def get_accounts(self, logins: list[str] | None = None) -> list[TradingAccount]:
        if logins:
            return [await self.get_account(login) for login in logins]
        data = await self._request("GET", "/trade/accounts")
        return [
            TradingAccount(
                account_id=f"TL-{a['id']}",
                platform=Platform.TRADE_LOCKER,
                login=str(a["id"]),
                name=a.get("name", ""),
                balance=float(a.get("balance", 0)),
                equity=float(a.get("equity", 0)),
                leverage=int(a.get("leverage", 100)),
                status=AccountStatus.ACTIVE if a.get("isActive") else AccountStatus.SUSPENDED,
            )
            for a in data.get("accounts", [])
        ]

    async def create_account(
        self, name: str, balance: float, leverage: int = 100,
        currency: str = "USD", group: str | None = None,
    ) -> AccountCredentials:
        data = await self._request("POST", "/trade/accounts", json={
            "name": name,
            "balance": balance,
            "leverage": leverage,
            "currency": currency,
            "group": group or "default",
        })
        return AccountCredentials(
            platform=Platform.TRADE_LOCKER,
            login=str(data["id"]),
            password=data.get("password"),
            server=self.server,
        )

    async def reset_account(self, login: str, new_balance: float) -> AccountResetResult:
        try:
            await self._request("POST", f"/trade/accounts/{login}/reset", json={
                "balance": new_balance,
            })
            return AccountResetResult(
                account_id=f"TL-{login}", platform=Platform.TRADE_LOCKER,
                success=True, new_balance=new_balance, reset_at=datetime.now(UTC),
            )
        except Exception as e:
            return AccountResetResult(
                account_id=f"TL-{login}", platform=Platform.TRADE_LOCKER,
                success=False, error=str(e),
            )

    async def get_open_positions(self, login: str) -> list[Position]:
        data = await self._request("GET", f"/trade/accounts/{login}/positions")
        return [
            Position(
                position_id=str(p["id"]),
                account_id=f"TL-{login}",
                platform=Platform.TRADE_LOCKER,
                symbol=p.get("tradableInstrumentId", ""),
                side=OrderSide.BUY if p.get("side") == "buy" else OrderSide.SELL,
                volume=float(p.get("qty", 0)),
                open_price=float(p.get("avgPrice", 0)),
                current_price=float(p.get("currentPrice", 0)),
                stop_loss=float(p["stopLoss"]) if p.get("stopLoss") else None,
                take_profit=float(p["takeProfit"]) if p.get("takeProfit") else None,
                profit=float(p.get("pnl", 0)),
                swap=float(p.get("swap", 0)),
                commission=float(p.get("commission", 0)),
            )
            for p in data.get("positions", [])
        ]

    async def get_trade_history(self, login: str, limit: int = 50, offset: int = 0) -> list[Trade]:
        data = await self._request("GET", f"/trade/accounts/{login}/orders", params={
            "limit": limit, "offset": offset, "status": "filled",
        })
        return [
            Trade(
                trade_id=str(t["id"]),
                account_id=f"TL-{login}",
                platform=Platform.TRADE_LOCKER,
                symbol=t.get("tradableInstrumentId", ""),
                side=OrderSide.BUY if t.get("side") == "buy" else OrderSide.SELL,
                volume=float(t.get("filledQty", 0)),
                open_price=float(t.get("avgFilledPrice", 0)),
                close_price=float(t.get("avgFilledPrice", 0)),
                profit=float(t.get("pnl", 0)),
            )
            for t in data.get("orders", [])
        ]

    async def get_platform_status(self) -> dict[str, Any]:
        try:
            data = await self._request("GET", "/trade/status")
            return {"platform": "trade_locker", "status": "operational", **data}
        except Exception as e:
            return {"platform": "trade_locker", "status": "degraded", "error": str(e)}
