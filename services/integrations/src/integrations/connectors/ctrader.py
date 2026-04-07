"""cTrader Open API connector."""

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


class CTraderConnector(BaseConnector):
    """Connector for cTrader via the Open API.

    cTrader uses OAuth2 for authentication and provides a REST API
    for account management and a WebSocket/Protobuf API for real-time data.

    Credentials dict expects:
    - api_url: cTrader Open API base URL
    - client_id: OAuth2 client ID
    - client_secret: OAuth2 client secret
    - access_token: Pre-obtained access token (or refresh flow)
    """

    platform = Platform.CTRADER
    name = "cTrader"
    description = "cTrader Open API connector for account and trade management"

    def __init__(self, credentials: dict[str, Any]):
        super().__init__(credentials)
        self.api_url = credentials.get("api_url", "https://api.ctrader.com")
        self.client_id = credentials.get("client_id", "")
        self.client_secret = credentials.get("client_secret", "")
        self.access_token = credentials.get("access_token", "")
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )
        await super().initialize()
        logger.info("ctrader_connector_initialized")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
        await super().close()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            raise RuntimeError("cTrader connector not initialized")
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_account(self, login: str) -> TradingAccount:
        data = await self._request("GET", f"/v2/accounts/{login}")
        return TradingAccount(
            account_id=f"CT-{login}",
            platform=Platform.CTRADER,
            login=login,
            server=data.get("brokerName"),
            name=data.get("traderName", ""),
            currency=data.get("depositCurrency", "USD"),
            balance=float(data.get("balance", 0)) / 100,  # cTrader uses cents
            equity=float(data.get("equity", 0)) / 100,
            margin=float(data.get("usedMargin", 0)) / 100,
            free_margin=float(data.get("freeMargin", 0)) / 100,
            profit=float(data.get("unrealizedPnl", 0)) / 100,
            leverage=int(data.get("leverageInCents", 10000) / 100),
            status=AccountStatus.ACTIVE if data.get("isEnabled") else AccountStatus.SUSPENDED,
        )

    async def get_accounts(self, logins: list[str] | None = None) -> list[TradingAccount]:
        if logins:
            return [await self.get_account(login) for login in logins]
        data = await self._request("GET", "/v2/accounts")
        return [
            TradingAccount(
                account_id=f"CT-{a['accountId']}",
                platform=Platform.CTRADER,
                login=str(a["accountId"]),
                name=a.get("traderName", ""),
                balance=float(a.get("balance", 0)) / 100,
                equity=float(a.get("equity", 0)) / 100,
                status=AccountStatus.ACTIVE,
            )
            for a in data.get("accounts", [])
        ]

    async def create_account(
        self, name: str, balance: float, leverage: int = 100,
        currency: str = "USD", group: str | None = None,
    ) -> AccountCredentials:
        data = await self._request("POST", "/v2/accounts", json={
            "traderName": name,
            "depositInCents": int(balance * 100),
            "leverageInCents": leverage * 100,
            "depositCurrency": currency,
            "groupName": group or "default",
        })
        return AccountCredentials(
            platform=Platform.CTRADER,
            login=str(data["accountId"]),
            password=data.get("password"),
            server=data.get("brokerName", ""),
        )

    async def reset_account(self, login: str, new_balance: float) -> AccountResetResult:
        try:
            await self._request("POST", f"/v2/accounts/{login}/reset", json={
                "balanceInCents": int(new_balance * 100),
            })
            return AccountResetResult(
                account_id=f"CT-{login}", platform=Platform.CTRADER,
                success=True, new_balance=new_balance, reset_at=datetime.now(UTC),
            )
        except Exception as e:
            return AccountResetResult(
                account_id=f"CT-{login}", platform=Platform.CTRADER,
                success=False, error=str(e),
            )

    async def get_open_positions(self, login: str) -> list[Position]:
        data = await self._request("GET", f"/v2/accounts/{login}/positions")
        return [
            Position(
                position_id=str(p["positionId"]),
                account_id=f"CT-{login}",
                platform=Platform.CTRADER,
                symbol=p.get("symbolName", ""),
                side=OrderSide.BUY if p.get("tradeSide") == "BUY" else OrderSide.SELL,
                volume=float(p.get("volume", 0)) / 100,
                open_price=float(p.get("entryPrice", 0)),
                current_price=float(p.get("currentPrice", 0)),
                stop_loss=float(p["stopLoss"]) if p.get("stopLoss") else None,
                take_profit=float(p["takeProfit"]) if p.get("takeProfit") else None,
                profit=float(p.get("pnl", 0)) / 100,
                swap=float(p.get("swap", 0)) / 100,
                commission=float(p.get("commission", 0)) / 100,
            )
            for p in data.get("positions", [])
        ]

    async def get_trade_history(self, login: str, limit: int = 50, offset: int = 0) -> list[Trade]:
        data = await self._request("GET", f"/v2/accounts/{login}/deals", params={
            "limit": limit, "offset": offset,
        })
        return [
            Trade(
                trade_id=str(d["dealId"]),
                account_id=f"CT-{login}",
                platform=Platform.CTRADER,
                symbol=d.get("symbolName", ""),
                side=OrderSide.BUY if d.get("tradeSide") == "BUY" else OrderSide.SELL,
                volume=float(d.get("volume", 0)) / 100,
                open_price=float(d.get("entryPrice", 0)),
                close_price=float(d.get("closePrice", 0)),
                profit=float(d.get("pnl", 0)) / 100,
                swap=float(d.get("swap", 0)) / 100,
                commission=float(d.get("commission", 0)) / 100,
            )
            for d in data.get("deals", [])
        ]

    async def get_platform_status(self) -> dict[str, Any]:
        try:
            data = await self._request("GET", "/v2/status")
            return {"platform": "ctrader", "status": "operational", **data}
        except Exception as e:
            return {"platform": "ctrader", "status": "degraded", "error": str(e)}
