"""Normalized trading data schemas — platform-agnostic models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Platform(str, Enum):
    MT4 = "mt4"
    MT5 = "mt5"
    CTRADER = "ctrader"
    MATCH_TRADER = "match_trader"
    TRADE_LOCKER = "trade_locker"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    PENDING = "pending"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    PARTIALLY_FILLED = "partially_filled"


class TradingAccount(BaseModel):
    """Normalized trading account data across all platforms."""
    account_id: str
    platform: Platform
    login: str
    server: str | None = None
    name: str | None = None
    currency: str = "USD"
    balance: float = 0.0
    equity: float = 0.0
    margin: float = 0.0
    free_margin: float = 0.0
    profit: float = 0.0
    leverage: int = 100
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Position(BaseModel):
    """Normalized open position."""
    position_id: str
    account_id: str
    platform: Platform
    symbol: str
    side: OrderSide
    volume: float
    open_price: float
    current_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    profit: float = 0.0
    swap: float = 0.0
    commission: float = 0.0
    opened_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Trade(BaseModel):
    """Normalized closed trade / deal."""
    trade_id: str
    account_id: str
    platform: Platform
    symbol: str
    side: OrderSide
    volume: float
    open_price: float
    close_price: float
    profit: float = 0.0
    swap: float = 0.0
    commission: float = 0.0
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AccountCredentials(BaseModel):
    """Credentials for creating / accessing a trading account."""
    platform: Platform
    login: str
    password: str | None = None
    server: str
    investor_password: str | None = None


class AccountResetResult(BaseModel):
    """Result of an account reset operation."""
    account_id: str
    platform: Platform
    success: bool
    new_balance: float | None = None
    reset_at: datetime | None = None
    error: str | None = None
