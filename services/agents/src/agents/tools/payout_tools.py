"""Payout agent tools — check eligibility, initiate payouts, get history."""

from typing import Any

from agents.tools.base import BaseTool, ToolContext, ToolResult


class CheckPayoutEligibility(BaseTool):
    name = "payout_check_eligibility"
    description = "Check if a trader is eligible for a payout based on their account status, profit targets, and compliance requirements."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "account_id": {"type": "string", "description": "Trading account ID to check"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"
    idempotency_key_fields = ["trader_id", "account_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        # TODO: Wire to actual trading platform connector
        # For now, return mock data that shows the structure
        return ToolResult(
            success=True,
            data={
                "eligible": True,
                "trader_id": params["trader_id"],
                "account_id": params.get("account_id", "default"),
                "min_trading_days_met": True,
                "profit_target_met": True,
                "no_rule_violations": True,
                "kyc_verified": True,
                "max_payout_amount": 5000.00,
                "next_payout_window": "2026-04-15",
                "profit_split_percent": 80,
            },
        )


class GetPayoutHistory(BaseTool):
    name = "payout_get_history"
    description = "Get the trader's payout history including past withdrawals, amounts, and statuses."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "limit": {"type": "integer", "description": "Number of records to return", "default": 10},
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
                "payouts": [
                    {
                        "id": "pay_001",
                        "amount": 2500.00,
                        "currency": "USD",
                        "method": "wire_transfer",
                        "status": "completed",
                        "requested_at": "2026-03-15T10:00:00Z",
                        "completed_at": "2026-03-18T14:30:00Z",
                    },
                    {
                        "id": "pay_002",
                        "amount": 1200.00,
                        "currency": "USD",
                        "method": "crypto_usdt",
                        "status": "completed",
                        "requested_at": "2026-02-20T09:00:00Z",
                        "completed_at": "2026-02-22T11:00:00Z",
                    },
                ],
                "total_paid_out": 3700.00,
            },
        )


class GetAccountBalance(BaseTool):
    name = "payout_get_balance"
    description = "Get the current balance and equity of a trading account."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "account_id": {"type": "string", "description": "Trading account ID"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"
    idempotency_key_fields = ["trader_id", "account_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "account_id": params.get("account_id", "default"),
                "balance": 12500.00,
                "equity": 12750.00,
                "profit": 2750.00,
                "margin_used": 450.00,
                "free_margin": 12300.00,
                "currency": "USD",
            },
        )


class InitiatePayout(BaseTool):
    name = "payout_initiate"
    description = "Initiate a payout request for a trader. This will create a pending payout that needs processing."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "amount": {"type": "number", "description": "Payout amount in USD"},
            "method": {
                "type": "string",
                "enum": ["wire_transfer", "crypto_usdt", "crypto_btc", "wise"],
                "description": "Payment method",
            },
        },
        "required": ["trader_id", "amount", "method"],
    }
    risk_level = "high"
    requires_approval = False  # Auto-approve below threshold; firm config controls this
    idempotency_key_fields = ["trader_id", "amount", "method"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        amount = params.get("amount", 0)
        if amount <= 0:
            return False
        if amount > 50000:  # Hard max
            return False
        return bool(params.get("trader_id") and params.get("method"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        amount = params["amount"]

        # Auto-approve threshold (from firm config in production)
        auto_approve_limit = 500.0
        needs_approval = amount > auto_approve_limit

        return ToolResult(
            success=True,
            data={
                "payout_id": "pay_new_001",
                "trader_id": params["trader_id"],
                "amount": amount,
                "method": params["method"],
                "status": "pending_approval" if needs_approval else "processing",
                "needs_human_approval": needs_approval,
                "estimated_completion": "2-3 business days",
            },
        )


class CheckPayoutStatus(BaseTool):
    name = "payout_check_status"
    description = "Check the current status of a specific payout request."
    parameters = {
        "type": "object",
        "properties": {
            "payout_id": {"type": "string", "description": "The payout request ID"},
        },
        "required": ["payout_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("payout_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "payout_id": params["payout_id"],
                "status": "processing",
                "amount": 2500.00,
                "method": "wire_transfer",
                "requested_at": "2026-04-05T10:00:00Z",
                "estimated_completion": "2026-04-08",
                "tracking_info": None,
            },
        )


class CancelPayout(BaseTool):
    name = "payout_cancel"
    description = "Cancel a pending payout request. Only works for payouts not yet processed."
    parameters = {
        "type": "object",
        "properties": {
            "payout_id": {"type": "string", "description": "The payout request ID to cancel"},
            "reason": {"type": "string", "description": "Reason for cancellation"},
        },
        "required": ["payout_id"],
    }
    risk_level = "high"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("payout_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "payout_id": params["payout_id"],
                "status": "cancelled",
                "reason": params.get("reason", "Trader requested cancellation"),
                "cancelled_at": "2026-04-07T12:00:00Z",
            },
        )


def get_payout_tools() -> list[BaseTool]:
    """Return all payout-related tools."""
    return [
        CheckPayoutEligibility(),
        GetPayoutHistory(),
        GetAccountBalance(),
        InitiatePayout(),
        CheckPayoutStatus(),
        CancelPayout(),
    ]
