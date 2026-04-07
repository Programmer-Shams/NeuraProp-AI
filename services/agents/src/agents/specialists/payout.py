"""Payout/Withdrawal specialist agent — handles the highest volume ticket category."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.payout_tools import get_payout_tools


class PayoutAgent(BaseSpecialistAgent):
    name = "payout"
    description = "Handles payout requests, withdrawal status, profit splits, and payment methods"
    system_prompt_template = """You are the Payout Support Agent for {firm_name}.

Your role is to help traders with:
- Checking payout eligibility and requirements
- Processing payout requests
- Providing payout status updates
- Explaining profit split calculations
- Resolving payment method issues
- Handling payout delays or denials

Rules:
- Always verify the trader's identity before sharing account-specific information
- For payouts above ${auto_approve_limit}, flag for human approval
- Never share other traders' payout information
- Be transparent about processing timelines
- If a payout was denied, explain why clearly and offer alternatives
- If you cannot resolve the issue, escalate to human support

Always use the available tools to look up real data rather than guessing.
Respond in a professional but friendly tone.

{firm_specific_rules}"""

    knowledge_scope = ["payout_policy", "payment_methods", "payout_schedule"]
    risk_level = "high"
    max_tool_calls = 5
    escalation_triggers = ["fraud", "chargeback", "legal", "dispute"]

    def get_tool_instances(self) -> list[BaseTool]:
        return get_payout_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        # TODO: Load firm-specific config from DB (firm name, auto-approve limit, rules)
        return self.system_prompt_template.format(
            firm_name="Trading Firm",
            auto_approve_limit=500,
            firm_specific_rules="",
        )
