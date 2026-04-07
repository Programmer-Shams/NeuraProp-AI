"""MT5 Manager API connector."""

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


class MT5Connector(BaseConnector):
    """Connector for MetaTrader 5 via the Manager API.

    MT5 Manager API provides REST endpoints through MetaApi, MT5 Web API,
    or the firm's own bridge service. The MT5 API is more structured than
    MT4 with better deal/position separation.

    Credentials dict expects:
    - api_url: Base URL of the MT5 Manager API
    - api_key: Authentication key / token
    - server: MT5 server name
    - manager_login: Manager account login
    """

    platform = Platform.MT5
    name = "MetaTrader 5"
    description = "MT5 Manager API connector for account and trade management"

    def __init__(self, credentials: dict[str, Any]):
        super().__init__(credentials)
        self.api_url = credentials.get("api_url", "")
        self.api_key = credentials.get("api_key", "")
        self.server = credentials.get("server", "")
        self.manager_login = credentials.get("manager_login", "")
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )
        await super().initialize()
        logger.info("mt5_connector_initialized", server=self.server)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
        await super().close()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            raise RuntimeError("MT5 connector not initialized")
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_account(self, login: str) -> TradingAccount:
        data = await self._request("GET", f"/api/accounts/{login}")
        return TradingAccount(
            account_id=f"MT5-{login}",
            platform=Platform.MT5,
            login=login,
            server=self.server,
            name=data.get("name", ""),
            currency=data.get("currency", "USD"),
            balance=float(data.get("balance", 0)),
            equity=float(data.get("equity", 0)),
            margin=float(data.get("margin", 0)),
            free_margin=float(data.get("margin_free", 0)),
            profit=float(data.get("profit", 0)),
            leverage=int(data.get("leverage", 100)),
            status=AccountStatus.ACTIVE if data.get("enable") else AccountStatus.SUSPENDED,
            metadata={"group": data.get("group", ""), "registration": data.get("registration")},
        )

    async def get_accounts(self, logins: list[str] | None = None) -> list[TradingAccount]:
        if logins:
            return [await self.get_account(login) for login in logins]
        data = await self._request("GET", "/api/accounts")
        return [
            TradingAccount(
                account_id=f"MT5-{a['login']}",
                platform=Platform.MT5,
                login=str(a["login"]),
                server=self.server,
                name=a.get("name", ""),
                balance=float(a.get("balance", 0)),
                equity=float(a.get("equity", 0)),
                leverage=int(a.get("leverage", 100)),
                status=AccountStatus.ACTIVE,
            )
            for a in data.get("accounts", [])
        ]

    async def create_account(
        self, name: str, balance: float, leverage: int = 100,
        currency: str = "USD", group: str | None = None,
    ) -> AccountCredentials:
        data = await self._request("POST", "/api/accounts", json={
            "name": name,
            "deposit": balance,
            "leverage": leverage,
            "currency": currency,
            "group": group or "default",
            "rights": 0x7FFFFFFF,  # Full trading rights
        })
        return AccountCredentials(
            platform=Platform.MT5,
            login=str(data["login"]),
            password=data.get("password"),
            server=self.server,
            investor_password=data.get("investor_password"),
        )

    async def reset_account(self, login: str, new_balance: float) -> AccountResetResult:
        try:
            # MT5 reset: close all positions, clear history, set new balance
            await self._request("POST", f"/api/accounts/{login}/reset", json={
                "new_balance": new_balance,
                "close_positions": True,
                "clear_history": True,
            })
            return AccountResetResult(
                account_id=f"MT5-{login}",
                platform=Platform.MT5,
                success=True,
                new_balance=new_balance,
                reset_at=datetime.now(UTC),
            )
        except Exception as e:
            return AccountResetResult(
                account_id=f"MT5-{login}", platform=Platform.MT5,
                success=False, error=str(e),
            )

    async def get_open_positions(self, login: str) -> list[Position]:
        data = await self._request("GET", f"/api/accounts/{login}/positions")
        return [
            Position(
                position_id=str(p["position"]),
                account_id=f"MT5-{login}",
                platform=Platform.MT5,
                symbol=p["symbol"],
                side=OrderSide.BUY if p.get("action", 0) == 0 else OrderSide.SELL,
                volume=float(p.get("volume", 0)),
                open_price=float(p.get("price_open", 0)),
                current_price=float(p.get("price_current", 0)),
                stop_loss=float(p["sl"]) if p.get("sl") else None,
                take_profit=float(p["tp"]) if p.get("tp") else None,
                profit=float(p.get("profit", 0)),
                swap=float(p.get("swap", 0)),
                commission=float(p.get("commission", 0)),
            )
            for p in data.get("positions", [])
        ]

    async def get_trade_history(self, login: str, limit: int = 50, offset: int = 0) -> list[Trade]:
        data = await self._request("GET", f"/api/accounts/{login}/deals", params={
            "limit": limit, "offset": offset,
        })
        return [
            Trade(
                trade_id=str(d["deal"]),
                account_id=f"MT5-{login}",
                platform=Platform.MT5,
                symbol=d.get("symbol", ""),
                side=OrderSide.BUY if d.get("action", 0) == 0 else OrderSide.SELL,
                volume=float(d.get("volume", 0)),
                open_price=float(d.get("price", 0)),
                close_price=float(d.get("price", 0)),
                profit=float(d.get("profit", 0)),
                swap=float(d.get("swap", 0)),
                commission=float(d.get("commission", 0)),
            )
            for d in data.get("deals", [])
        ]

    async def get_platform_status(self) -> dict[str, Any]:
        try:
            data = await self._request("GET", "/api/status")
            return {"platform": "mt5", "status": "operational", **data}
        except Exception as e:
            return {"platform": "mt5", "status": "degraded", "error": str(e)}
