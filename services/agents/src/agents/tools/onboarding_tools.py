"""Onboarding tools — challenge listing, account creation, welcome flows."""

from agents.tools.base import BaseTool, ToolContext, ToolResult


class GetAvailableChallenges(BaseTool):
    name = "onboarding_get_challenges"
    description = "List all available challenge types with pricing and requirements."
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return True

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "challenges": [
                {"type": "standard", "sizes": ["10k", "25k", "50k", "100k", "200k"], "phases": 2, "profit_target_p1": "8%", "profit_target_p2": "5%", "price_from": 99},
                {"type": "aggressive", "sizes": ["10k", "25k", "50k", "100k"], "phases": 1, "profit_target": "10%", "price_from": 149},
                {"type": "instant_funded", "sizes": ["5k", "10k", "25k"], "phases": 0, "price_from": 249},
            ],
        })


class CreateChallengeAccount(BaseTool):
    name = "onboarding_create_account"
    description = "Create a new challenge account for a trader."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "challenge_type": {"type": "string", "enum": ["standard", "aggressive", "instant_funded"]},
            "account_size": {"type": "string", "enum": ["5k", "10k", "25k", "50k", "100k", "200k"]},
            "platform": {"type": "string", "enum": ["mt4", "mt5", "ctrader"]},
        },
        "required": ["trader_id", "challenge_type", "account_size", "platform"],
    }
    risk_level = "medium"
    idempotency_key_fields = ["trader_id", "challenge_type", "account_size"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return all(params.get(f) for f in ["trader_id", "challenge_type", "account_size", "platform"])

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "account_id": "MT5-NEW-001",
            "trader_id": params["trader_id"],
            "challenge_type": params["challenge_type"],
            "account_size": params["account_size"],
            "platform": params["platform"],
            "status": "pending_payment",
            "credentials_sent": False,
        })


class SendWelcomeEmail(BaseTool):
    name = "onboarding_send_welcome"
    description = "Send welcome email with setup instructions and getting-started guide."
    parameters = {
        "type": "object",
        "properties": {"trader_id": {"type": "string"}},
        "required": ["trader_id"],
    }
    risk_level = "low"
    idempotency_key_fields = ["trader_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "trader_id": params["trader_id"],
            "email_sent": True,
            "template": "welcome_v2",
        })


class GeneratePlatformCredentials(BaseTool):
    name = "onboarding_generate_credentials"
    description = "Generate trading platform login credentials for a trader's account."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "account_id": {"type": "string"},
            "platform": {"type": "string", "enum": ["mt4", "mt5", "ctrader"]},
        },
        "required": ["trader_id", "account_id", "platform"],
    }
    risk_level = "medium"
    idempotency_key_fields = ["trader_id", "account_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("account_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "account_id": params["account_id"],
            "platform": params["platform"],
            "server": "NeuraProp-Live",
            "login": "12345678",
            "credentials_sent_via": "email",
        })


def get_onboarding_tools() -> list[BaseTool]:
    return [GetAvailableChallenges(), CreateChallengeAccount(), SendWelcomeEmail(), GeneratePlatformCredentials()]
