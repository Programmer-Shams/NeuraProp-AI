"""Payout/Withdrawal specialist agent — handles the highest volume ticket category."""

from typing import Any

from agents.specialists.base import BaseSpecialistAgent


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
- If you cannot resolve the issue, escalate to human support

{firm_specific_rules}"""

    knowledge_scope = ["payout_policy", "payment_methods", "payout_schedule"]
    risk_level = "high"
    max_tool_calls = 5
    escalation_triggers = ["fraud", "chargeback", "legal"]

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "check_payout_eligibility", "description": "Check if trader is eligible for payout"},
            {"name": "get_payout_history", "description": "Get trader's payout history"},
            {"name": "get_account_balance", "description": "Get current account balance"},
            {"name": "initiate_payout", "description": "Initiate a payout request"},
            {"name": "check_payout_status", "description": "Check status of a pending payout"},
            {"name": "cancel_payout", "description": "Cancel a pending payout request"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        # TODO: Load firm-specific config from DB
        return self.system_prompt_template.format(
            firm_name="Trading Firm",
            auto_approve_limit=500,
            firm_specific_rules="",
        )
