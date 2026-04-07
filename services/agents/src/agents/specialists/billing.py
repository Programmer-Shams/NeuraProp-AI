"""Billing/Refund specialist agent."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.billing_tools import get_billing_tools


class BillingAgent(BaseSpecialistAgent):
    name = "billing"
    description = "Handles billing questions, refund requests, subscription management, fee inquiries"
    system_prompt_template = """You are the Billing & Refund Agent for {firm_name}.

Help traders with billing inquiries, refund processing, subscription management,
and fee explanations. Always verify eligibility before processing refunds.

{firm_specific_rules}"""

    knowledge_scope = ["pricing", "refund_policy", "promotion_terms"]
    risk_level = "high"
    max_tool_calls = 5
    escalation_triggers = ["chargeback", "fraud", "unauthorized"]

    def get_tool_instances(self) -> list[BaseTool]:
        return get_billing_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
