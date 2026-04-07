"""Tests for universal API connector — JSONPath extraction and action mapping."""

import pytest

from integrations.connectors.universal import (
    _extract_jsonpath,
    ActionMapping,
    UniversalConnector,
)


class TestExtractJsonpath:
    def test_simple_key(self):
        data = {"balance": 5000}
        assert _extract_jsonpath(data, "$.balance") == 5000

    def test_nested_key(self):
        data = {"data": {"account": {"balance": 3200}}}
        assert _extract_jsonpath(data, "$.data.account.balance") == 3200

    def test_array_index(self):
        data = {"accounts": [{"id": "a"}, {"id": "b"}]}
        assert _extract_jsonpath(data, "$.accounts[0]") == {"id": "a"}
        assert _extract_jsonpath(data, "$.accounts[1]") == {"id": "b"}

    def test_array_wildcard(self):
        data = {"trades": [{"symbol": "EURUSD"}, {"symbol": "GBPUSD"}]}
        result = _extract_jsonpath(data, "$.trades[*]")
        assert len(result) == 2

    def test_nested_array_field(self):
        data = {"data": {"items": [{"name": "a"}, {"name": "b"}]}}
        result = _extract_jsonpath(data, "$.data.items[0]")
        assert result == {"name": "a"}

    def test_missing_key_returns_none(self):
        data = {"foo": "bar"}
        assert _extract_jsonpath(data, "$.missing") is None

    def test_missing_nested_returns_none(self):
        data = {"a": {"b": 1}}
        assert _extract_jsonpath(data, "$.a.c.d") is None

    def test_out_of_bounds_returns_none(self):
        data = {"items": [1, 2]}
        assert _extract_jsonpath(data, "$.items[5]") is None

    def test_non_jsonpath_returns_data(self):
        data = {"key": "value"}
        assert _extract_jsonpath(data, "key") == data

    def test_empty_data(self):
        assert _extract_jsonpath({}, "$.key") is None

    def test_deeply_nested(self):
        data = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        assert _extract_jsonpath(data, "$.a.b.c.d.e") == 42


class TestActionMapping:
    def test_creates_mapping(self):
        mapping = ActionMapping(
            action_name="get_balance",
            method="GET",
            path_template="/api/accounts/{{ login }}/balance",
        )
        assert mapping.action_name == "get_balance"
        assert mapping.method == "GET"

    def test_renders_path_template(self):
        mapping = ActionMapping(
            action_name="get_account",
            method="GET",
            path_template="/api/accounts/{{ account_id }}/details",
        )
        rendered = mapping.path_template.render(account_id="ACC-123")
        assert rendered == "/api/accounts/ACC-123/details"

    def test_renders_body_template(self):
        mapping = ActionMapping(
            action_name="create_account",
            method="POST",
            path_template="/api/accounts",
            body_template='{"name": "{{ name }}", "balance": {{ balance }}}',
        )
        rendered = mapping.body_template.render(name="Test Account", balance=10000)
        assert '"name": "Test Account"' in rendered
        assert '"balance": 10000' in rendered

    def test_default_headers(self):
        mapping = ActionMapping(
            action_name="test",
            method="GET",
            path_template="/test",
        )
        assert mapping.headers == {}

    def test_custom_headers(self):
        mapping = ActionMapping(
            action_name="test",
            method="GET",
            path_template="/test",
            headers={"X-Custom": "value"},
        )
        assert mapping.headers["X-Custom"] == "value"


class TestUniversalConnector:
    def test_init_parses_mappings(self):
        connector = UniversalConnector(
            base_url="https://api.example.com",
            auth_headers={"Authorization": "Bearer test"},
            action_mappings=[
                {
                    "action_name": "get_balance",
                    "method": "GET",
                    "path_template": "/accounts/{{ id }}/balance",
                    "response_mapping": {
                        "balance": "$.data.balance",
                        "currency": "$.data.currency",
                    },
                },
                {
                    "action_name": "reset_account",
                    "method": "POST",
                    "path_template": "/accounts/{{ id }}/reset",
                    "body_template": '{"reason": "{{ reason }}"}',
                },
            ],
        )

        assert connector.list_actions() == ["get_balance", "reset_account"]

    def test_not_initialized_raises(self):
        connector = UniversalConnector(
            base_url="https://api.example.com",
            auth_headers={},
            action_mappings=[],
        )
        # Client not initialized yet
        assert connector._client is None

    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        connector = UniversalConnector(
            base_url="https://api.example.com",
            auth_headers={},
            action_mappings=[],
        )
        # Mock the client so it doesn't fail on initialization check
        import httpx
        connector._client = httpx.AsyncClient(base_url="https://api.example.com")

        result = await connector.execute_action("nonexistent", {})
        assert result["success"] is False
        assert "Unknown action" in result["error"]

        await connector._client.aclose()


class TestTradingSchemas:
    def test_platform_enum(self):
        from integrations.schemas.trading import Platform

        assert Platform.MT4 == "mt4"
        assert Platform.MT5 == "mt5"
        assert Platform.CTRADER == "ctrader"
        assert Platform.MATCH_TRADER == "match_trader"
        assert Platform.TRADE_LOCKER == "trade_locker"

    def test_trading_account_model(self):
        from integrations.schemas.trading import TradingAccount, Platform

        account = TradingAccount(
            account_id="ACC-1",
            platform=Platform.MT5,
            login="12345",
            server="demo.server.com",
            currency="USD",
            balance=10000.0,
            equity=10500.0,
            leverage=100,
        )
        assert account.platform == Platform.MT5
        assert account.balance == 10000.0

    def test_position_model(self):
        from integrations.schemas.trading import Position, Platform, OrderSide

        pos = Position(
            position_id="POS-1",
            account_id="ACC-1",
            platform=Platform.MT5,
            symbol="EURUSD",
            side=OrderSide.BUY,
            volume=1.0,
            open_price=1.0850,
            profit=120.50,
        )
        assert pos.side == OrderSide.BUY
        assert pos.profit == 120.50

    def test_trade_model(self):
        from integrations.schemas.trading import Trade, Platform, OrderSide

        trade = Trade(
            trade_id="TRD-1",
            account_id="ACC-1",
            platform=Platform.CTRADER,
            symbol="GBPUSD",
            side=OrderSide.SELL,
            volume=0.5,
            open_price=1.2650,
            close_price=1.2600,
            profit=250.00,
        )
        assert trade.close_price == 1.2600
        assert trade.platform == Platform.CTRADER

    def test_account_reset_result(self):
        from integrations.schemas.trading import AccountResetResult, Platform

        result = AccountResetResult(
            account_id="ACC-1",
            platform=Platform.MT4,
            success=True,
            new_balance=50000.0,
        )
        assert result.success is True
        assert result.new_balance == 50000.0

    def test_kyc_schemas(self):
        from integrations.schemas.kyc import VerificationStatus, DocumentType

        assert VerificationStatus.APPROVED == "approved"
        assert DocumentType.PASSPORT == "passport"
