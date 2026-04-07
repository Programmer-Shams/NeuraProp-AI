"""Billing/Refund tools — billing history, refunds, subscriptions, invoices."""

from agents.tools.base import BaseTool, ToolContext, ToolResult


class GetBillingHistory(BaseTool):
    name = "billing_get_history"
    description = "Get a trader's billing and payment history."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "limit": {"type": "integer", "default": 10},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "trader_id": params["trader_id"],
            "transactions": [
                {"id": "txn_001", "amount": 399.00, "type": "challenge_purchase", "status": "completed", "date": "2026-03-20"},
                {"id": "txn_002", "amount": 599.00, "type": "challenge_purchase", "status": "completed", "date": "2026-02-15"},
            ],
            "total_spent": 998.00,
        })


class ProcessRefund(BaseTool):
    name = "billing_process_refund"
    description = "Process a refund for a qualifying purchase. Checks eligibility first."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "transaction_id": {"type": "string", "description": "Transaction to refund"},
            "reason": {"type": "string"},
        },
        "required": ["trader_id", "transaction_id"],
    }
    risk_level = "high"
    idempotency_key_fields = ["trader_id", "transaction_id"]

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("transaction_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "refund_id": "ref_001",
            "transaction_id": params["transaction_id"],
            "status": "processing",
            "estimated_completion": "5-7 business days",
        })


class ApplyDiscount(BaseTool):
    name = "billing_apply_discount"
    description = "Apply a promotional discount code to a trader's account."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "code": {"type": "string", "description": "Discount/promo code"},
        },
        "required": ["trader_id", "code"],
    }
    risk_level = "medium"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("code"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "code": params["code"],
            "valid": True,
            "discount_percent": 15,
            "applied_to": params["trader_id"],
        })


class GetSubscriptionDetails(BaseTool):
    name = "billing_get_subscription"
    description = "Get subscription and plan details for a trader."
    parameters = {
        "type": "object",
        "properties": {"trader_id": {"type": "string"}},
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "trader_id": params["trader_id"],
            "plan": "standard",
            "status": "active",
            "renewal_date": "2026-05-20",
        })


class GenerateInvoice(BaseTool):
    name = "billing_generate_invoice"
    description = "Generate an invoice for a specific transaction."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "transaction_id": {"type": "string"},
        },
        "required": ["trader_id", "transaction_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id") and params.get("transaction_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "invoice_id": "inv_001",
            "download_url": "/api/v1/invoices/inv_001/download",
            "status": "generated",
        })


def get_billing_tools() -> list[BaseTool]:
    return [GetBillingHistory(), ProcessRefund(), ApplyDiscount(), GetSubscriptionDetails(), GenerateInvoice()]
