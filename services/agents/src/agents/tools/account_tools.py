"""Account/KYC agent tools — manage accounts, KYC verification, identity."""

from agents.tools.base import BaseTool, ToolContext, ToolResult


class GetKYCStatus(BaseTool):
    name = "account_get_kyc_status"
    description = "Check the current KYC verification status for a trader."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "kyc_status": "verified",
                "verification_date": "2026-03-10",
                "documents_submitted": ["passport", "proof_of_address"],
                "next_review_date": None,
            },
        )


class InitiateKYC(BaseTool):
    name = "account_initiate_kyc"
    description = "Start or restart the KYC verification process for a trader. Generates a verification link."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "document_type": {
                "type": "string",
                "enum": ["passport", "id_card", "drivers_license"],
                "description": "Type of identity document",
            },
        },
        "required": ["trader_id"],
    }
    risk_level = "medium"
    idempotency_key_fields = ["trader_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "verification_session_id": "kyc_sess_001",
                "verification_url": "https://verify.example.com/session/kyc_sess_001",
                "expires_at": "2026-04-08T12:00:00Z",
                "status": "pending",
            },
        )


class ResetAccount(BaseTool):
    name = "account_reset"
    description = "Reset a trading account (challenge restart). This will reset the balance and trading history."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "account_id": {"type": "string", "description": "Trading account to reset"},
            "reason": {"type": "string", "description": "Reason for reset"},
        },
        "required": ["trader_id", "account_id"],
    }
    risk_level = "high"
    idempotency_key_fields = ["trader_id", "account_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("account_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "account_id": params["account_id"],
                "status": "reset_complete",
                "new_balance": 50000.00,
                "reset_at": "2026-04-07T12:00:00Z",
                "reason": params.get("reason", "Trader requested reset"),
            },
        )


class GetTraderAccounts(BaseTool):
    name = "account_get_accounts"
    description = "List all trading accounts linked to a trader."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "accounts": [
                    {
                        "account_id": "MT5-12345",
                        "platform": "mt5",
                        "type": "funded",
                        "size": 50000,
                        "status": "active",
                        "balance": 53200.00,
                    },
                    {
                        "account_id": "MT5-12346",
                        "platform": "mt5",
                        "type": "challenge_phase1",
                        "size": 100000,
                        "status": "active",
                        "balance": 101500.00,
                    },
                ],
            },
        )


class UpdateTraderProfile(BaseTool):
    name = "account_update_profile"
    description = "Update trader profile information such as email, display name, or payment preferences."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "email": {"type": "string", "description": "New email address"},
            "display_name": {"type": "string", "description": "New display name"},
            "preferred_payment_method": {
                "type": "string",
                "enum": ["wire_transfer", "crypto_usdt", "crypto_btc", "wise"],
            },
        },
        "required": ["trader_id"],
    }
    risk_level = "medium"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        updated_fields = {k: v for k, v in params.items() if k != "trader_id" and v}
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "updated_fields": list(updated_fields.keys()),
                "status": "updated",
            },
        )


class LinkTradingAccount(BaseTool):
    name = "account_link"
    description = "Link a new trading platform account to the trader's profile."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "platform": {"type": "string", "enum": ["mt4", "mt5", "ctrader"]},
            "account_number": {"type": "string", "description": "Platform account number"},
        },
        "required": ["trader_id", "platform", "account_number"],
    }
    risk_level = "medium"
    idempotency_key_fields = ["trader_id", "platform", "account_number"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return all(params.get(f) for f in ["trader_id", "platform", "account_number"])

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "account_id": f"{params['platform'].upper()}-{params['account_number']}",
                "platform": params["platform"],
                "status": "linked",
            },
        )


def get_account_tools() -> list[BaseTool]:
    return [
        GetKYCStatus(),
        InitiateKYC(),
        ResetAccount(),
        GetTraderAccounts(),
        UpdateTraderProfile(),
        LinkTradingAccount(),
    ]
