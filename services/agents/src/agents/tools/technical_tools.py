"""Technical support tools — platform status, execution checks, credentials."""

from agents.tools.base import BaseTool, ToolContext, ToolResult


class CheckPlatformStatus(BaseTool):
    name = "technical_check_platform_status"
    description = "Check the current status of a trading platform (MT4, MT5, cTrader) including any known outages or maintenance."
    parameters = {
        "type": "object",
        "properties": {
            "platform": {"type": "string", "enum": ["mt4", "mt5", "ctrader"], "description": "Trading platform"},
        },
        "required": ["platform"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("platform"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "platform": params["platform"],
            "status": "operational",
            "uptime_24h": "99.98%",
            "known_issues": [],
            "last_maintenance": "2026-04-01T02:00:00Z",
        })


class CheckTradeExecution(BaseTool):
    name = "technical_check_execution"
    description = "Verify details of a specific trade execution including fill price, slippage, and timing."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "order_id": {"type": "string", "description": "The order/trade ID to check"},
        },
        "required": ["trader_id", "order_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("order_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "order_id": params["order_id"],
            "status": "filled",
            "symbol": "EURUSD",
            "type": "buy",
            "requested_price": 1.08500,
            "fill_price": 1.08502,
            "slippage_pips": 0.2,
            "fill_time_ms": 45,
            "timestamp": "2026-04-06T14:30:00Z",
        })


class VerifyCredentials(BaseTool):
    name = "technical_verify_credentials"
    description = "Verify that a trader's platform credentials are valid and the account is accessible."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "platform": {"type": "string", "enum": ["mt4", "mt5", "ctrader"]},
        },
        "required": ["trader_id", "platform"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("platform"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "trader_id": params["trader_id"],
            "platform": params["platform"],
            "credentials_valid": True,
            "last_login": "2026-04-06T18:00:00Z",
            "account_accessible": True,
        })


class SubmitTechnicalTicket(BaseTool):
    name = "technical_submit_ticket"
    description = "Submit a technical investigation ticket for issues that need backend investigation."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "issue_type": {"type": "string", "description": "Type of technical issue"},
            "description": {"type": "string", "description": "Detailed description of the issue"},
        },
        "required": ["trader_id", "issue_type", "description"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return all(params.get(f) for f in ["trader_id", "issue_type", "description"])

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "ticket_id": "TECH-001",
            "status": "open",
            "priority": "medium",
            "estimated_response": "24 hours",
        })


def get_technical_tools() -> list[BaseTool]:
    return [CheckPlatformStatus(), CheckTradeExecution(), VerifyCredentials(), SubmitTechnicalTicket()]
