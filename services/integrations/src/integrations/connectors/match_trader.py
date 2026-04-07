"""Match-Trader API connector."""

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


class MatchTraderConnector(BaseConnector):
    """Connector for Match-Trader platform.

    Match-Trader provides a REST API for prop firms with built-in
    challenge management, account creation, and risk monitoring.

    Credentials dict expects:
    - api_url: Match-Trader API base URL
    - api_key: API key
    - broker_id: Broker identifier
    """

    platform = Platform.MATCH_TRADER
    name = "Match-Trader"
    description = "Match-Trader API connector for prop firm account management"

    def __init__(self, credentials: dict[str, Any]):
        super().__init__(credentials)
        self.api_url = credentials.get("api_url", "")
        self.api_key = credentials.get("api_key", "")
        self.broker_id = credentials.get("broker_id", "")
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "X-API-Key": self.api_key,
                "X-Broker-ID": self.broker_id,
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )
        await super().initialize()
        logger.info("match_trader_connector_initialized", broker=self.broker_id)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
        await super().close()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            raise RuntimeError("Match-Trader connector not initialized")
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_account(self, login: str) -> TradingAccount:
        data = await self._request("GET", f"/api/v1/accounts/{login}")
        return TradingAccount(
            account_id=f"MATCH-{login}",
            platform=Platform.MATCH_TRADER,
            login=login,
            server=self.broker_id,
            name=data.get("accountName", ""),
            currency=data.get("currency", "USD"),
            balance=float(data.get("balance", 0)),
            equity=float(data.get("equity", 0)),
            margin=float(data.get("usedMargin", 0)),
            free_margin=float(data.get("freeMargin", 0)),
            profit=float(data.get("unrealizedPnl", 0)),
            leverage=int(data.get("leverage", 100)),
            status=AccountStatus(data.get("status", "active")),
            metadata={
                "challenge_type": data.get("challengeType"),
                "phase": data.get("phase"),
                "profit_target": data.get("profitTarget"),
                "max_drawdown": data.get("maxDrawdown"),
            },
        )

    async def get_accounts(self, logins: list[str] | None = None) -> list[TradingAccount]:
        if logins:
            return [await self.get_account(login) for login in logins]
        data = await self._request("GET", "/api/v1/accounts")
        return [
            TradingAccount(
                account_id=f"MATCH-{a['accountId']}",
                platform=Platform.MATCH_TRADER,
                login=str(a["accountId"]),
                name=a.get("accountName", ""),
                balance=float(a.get("balance", 0)),
                equity=float(a.get("equity", 0)),
                leverage=int(a.get("leverage", 100)),
                status=AccountStatus(a.get("status", "active")),
            )
            for a in data.get("accounts", [])
        ]

    async def create_account(
        self, name: str, balance: float, leverage: int = 100,
        currency: str = "USD", group: str | None = None,
    ) -> AccountCredentials:
        data = await self._request("POST", "/api/v1/accounts", json={
            "accountName": name,
            "initialBalance": balance,
            "leverage": leverage,
            "currency": currency,
            "challengeType": group or "standard",
        })
        return AccountCredentials(
            platform=Platform.MATCH_TRADER,
            login=str(data["accountId"]),
            password=data.get("password"),
            server=self.broker_id,
        )

    async def reset_account(self, login: str, new_balance: float) -> AccountResetResult:
        try:
            await self._request("POST", f"/api/v1/accounts/{login}/reset", json={
                "newBalance": new_balance,
            })
            return AccountResetResult(
                account_id=f"MATCH-{login}", platform=Platform.MATCH_TRADER,
                success=True, new_balance=new_balance, reset_at=datetime.now(UTC),
            )
        except Exception as e:
            return AccountResetResult(
                account_id=f"MATCH-{login}", platform=Platform.MATCH_TRADER,
                success=False, error=str(e),
            )

    async def get_open_positions(self, login: str) -> list[Position]:
        data = await self._request("GET", f"/api/v1/accounts/{login}/positions")
        return [
            Position(
                position_id=str(p["positionId"]),
                account_id=f"MATCH-{login}",
                platform=Platform.MATCH_TRADER,
                symbol=p.get("symbol", ""),
                side=OrderSide.BUY if p.get("side") == "buy" else OrderSide.SELL,
                volume=float(p.get("lots", 0)),
                open_price=float(p.get("openPrice", 0)),
                current_price=float(p.get("currentPrice", 0)),
                stop_loss=float(p["stopLoss"]) if p.get("stopLoss") else None,
                take_profit=float(p["takeProfit"]) if p.get("takeProfit") else None,
                profit=float(p.get("profit", 0)),
                swap=float(p.get("swap", 0)),
                commission=float(p.get("commission", 0)),
            )
            for p in data.get("positions", [])
        ]

    async def get_trade_history(self, login: str, limit: int = 50, offset: int = 0) -> list[Trade]:
        data = await self._request("GET", f"/api/v1/accounts/{login}/trades", params={
            "limit": limit, "offset": offset,
        })
        return [
            Trade(
                trade_id=str(t["tradeId"]),
                account_id=f"MATCH-{login}",
                platform=Platform.MATCH_TRADER,
                symbol=t.get("symbol", ""),
                side=OrderSide.BUY if t.get("side") == "buy" else OrderSide.SELL,
                volume=float(t.get("lots", 0)),
                open_price=float(t.get("openPrice", 0)),
                close_price=float(t.get("closePrice", 0)),
                profit=float(t.get("profit", 0)),
                swap=float(t.get("swap", 0)),
                commission=float(t.get("commission", 0)),
            )
            for t in data.get("trades", [])
        ]

    async def get_platform_status(self) -> dict[str, Any]:
        try:
            data = await self._request("GET", "/api/v1/status")
            return {"platform": "match_trader", "status": "operational", **data}
        except Exception as e:
            return {"platform": "match_trader", "status": "degraded", "error": str(e)}
