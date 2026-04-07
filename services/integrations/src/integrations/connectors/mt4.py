"""MT4 Manager API connector."""

from datetime import datetime, UTC
from typing import Any

import httpx

from neuraprop_core.logging import get_logger

from integrations.connectors.base import BaseConnector
from integrations.schemas.trading import (
    TradingAccount, Position, Trade, AccountCredentials,
    AccountResetResult, Platform, AccountStatus, OrderSide, OrderStatus,
)

logger = get_logger(__name__)


class MT4Connector(BaseConnector):
    """Connector for MetaTrader 4 via the Manager API.

    MT4 Manager API is typically accessed through a web API wrapper
    (e.g., MT4 Web API, or a proprietary bridge) since the native
    Manager API is a Windows COM/DLL interface.

    Credentials dict expects:
    - api_url: Base URL of the MT4 Manager API bridge
    - api_key: Authentication key
    - server: MT4 server name
    """

    platform = Platform.MT4
    name = "MetaTrader 4"
    description = "MT4 Manager API connector for account and trade management"

    def __init__(self, credentials: dict[str, Any]):
        super().__init__(credentials)
        self.api_url = credentials.get("api_url", "")
        self.api_key = credentials.get("api_key", "")
        self.server = credentials.get("server", "")
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=15.0,
        )
        await super().initialize()
        logger.info("mt4_connector_initialized", server=self.server)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
        await super().close()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            raise RuntimeError("MT4 connector not initialized")
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_account(self, login: str) -> TradingAccount:
        data = await self._request("GET", f"/accounts/{login}")
        return TradingAccount(
            account_id=f"MT4-{login}",
            platform=Platform.MT4,
            login=login,
            server=self.server,
            name=data.get("name", ""),
            currency=data.get("currency", "USD"),
            balance=float(data.get("balance", 0)),
            equity=float(data.get("equity", 0)),
            margin=float(data.get("margin", 0)),
            free_margin=float(data.get("free_margin", 0)),
            profit=float(data.get("profit", 0)),
            leverage=int(data.get("leverage", 100)),
            status=AccountStatus.ACTIVE if data.get("enable") else AccountStatus.SUSPENDED,
        )

    async def get_accounts(self, logins: list[str] | None = None) -> list[TradingAccount]:
        if logins:
            return [await self.get_account(login) for login in logins]
        data = await self._request("GET", "/accounts")
        return [
            TradingAccount(
                account_id=f"MT4-{a['login']}",
                platform=Platform.MT4,
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
        data = await self._request("POST", "/accounts", json={
            "name": name,
            "deposit": balance,
            "leverage": leverage,
            "currency": currency,
            "group": group or "default",
        })
        return AccountCredentials(
            platform=Platform.MT4,
            login=str(data["login"]),
            password=data.get("password"),
            server=self.server,
            investor_password=data.get("investor_password"),
        )

    async def reset_account(self, login: str, new_balance: float) -> AccountResetResult:
        try:
            await self._request("POST", f"/accounts/{login}/reset", json={
                "new_balance": new_balance,
            })
            return AccountResetResult(
                account_id=f"MT4-{login}",
                platform=Platform.MT4,
                success=True,
                new_balance=new_balance,
                reset_at=datetime.now(UTC),
            )
        except Exception as e:
            return AccountResetResult(
                account_id=f"MT4-{login}",
                platform=Platform.MT4,
                success=False,
                error=str(e),
            )

    async def get_open_positions(self, login: str) -> list[Position]:
        data = await self._request("GET", f"/accounts/{login}/positions")
        return [
            Position(
                position_id=str(p["ticket"]),
                account_id=f"MT4-{login}",
                platform=Platform.MT4,
                symbol=p["symbol"],
                side=OrderSide.BUY if p.get("cmd", 0) == 0 else OrderSide.SELL,
                volume=float(p.get("volume", 0)) / 100,  # MT4 uses lots * 100
                open_price=float(p.get("open_price", 0)),
                current_price=float(p.get("close_price", 0)),
                stop_loss=float(p["sl"]) if p.get("sl") else None,
                take_profit=float(p["tp"]) if p.get("tp") else None,
                profit=float(p.get("profit", 0)),
                swap=float(p.get("swap", 0)),
                commission=float(p.get("commission", 0)),
            )
            for p in data.get("positions", [])
        ]

    async def get_trade_history(self, login: str, limit: int = 50, offset: int = 0) -> list[Trade]:
        data = await self._request("GET", f"/accounts/{login}/trades", params={
            "limit": limit, "offset": offset,
        })
        return [
            Trade(
                trade_id=str(t["ticket"]),
                account_id=f"MT4-{login}",
                platform=Platform.MT4,
                symbol=t["symbol"],
                side=OrderSide.BUY if t.get("cmd", 0) == 0 else OrderSide.SELL,
                volume=float(t.get("volume", 0)) / 100,
                open_price=float(t.get("open_price", 0)),
                close_price=float(t.get("close_price", 0)),
                profit=float(t.get("profit", 0)),
                swap=float(t.get("swap", 0)),
                commission=float(t.get("commission", 0)),
            )
            for t in data.get("trades", [])
        ]

    async def get_platform_status(self) -> dict[str, Any]:
        try:
            data = await self._request("GET", "/status")
            return {"platform": "mt4", "status": "operational", **data}
        except Exception as e:
            return {"platform": "mt4", "status": "degraded", "error": str(e)}
