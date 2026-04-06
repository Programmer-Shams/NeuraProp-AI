"""Billing/Refund specialist agent."""

from typing import Any
from agents.specialists.base import BaseSpecialistAgent


class BillingAgent(BaseSpecialistAgent):
    name = "billing"
    description = "Handles billing questions, refund requests, subscription management, fee inquiries"
    system_prompt_template = """You are the Billing & Refund Agent for {firm_name}.

Help traders with billing inquiries, refund processing, subscription management,
and fee explanations. Always verify eligibility before processing refunds.

{firm_specific_rules}"""

    knowledge_scope = ["pricing", "refund_policy", "promotion_terms"]
    risk_level = "high"

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "get_billing_history", "description": "Get trader's billing history"},
            {"name": "get_subscription_details", "description": "Get subscription details"},
            {"name": "process_refund", "description": "Process a refund request"},
            {"name": "apply_discount_code", "description": "Apply a discount/promo code"},
            {"name": "generate_invoice", "description": "Generate an invoice"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
