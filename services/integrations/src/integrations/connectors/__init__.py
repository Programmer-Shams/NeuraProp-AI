"""Platform connectors — MT4, MT5, cTrader, Match-Trader, TradeLocker, Veriff, Universal."""

from integrations.connectors.base import BaseConnector, ConnectorRegistry, get_connector_registry
from integrations.connectors.mt4 import MT4Connector
from integrations.connectors.mt5 import MT5Connector
from integrations.connectors.ctrader import CTraderConnector
from integrations.connectors.match_trader import MatchTraderConnector
from integrations.connectors.trade_locker import TradeLockerConnector
from integrations.connectors.veriff import VeriffConnector
from integrations.connectors.universal import UniversalConnector

__all__ = [
    "BaseConnector",
    "ConnectorRegistry",
    "get_connector_registry",
    "MT4Connector",
    "MT5Connector",
    "CTraderConnector",
    "MatchTraderConnector",
    "TradeLockerConnector",
    "VeriffConnector",
    "UniversalConnector",
]
