"""Account/KYC specialist agent."""

from typing import Any

from agents.specialists.base import BaseSpecialistAgent


class AccountKYCAgent(BaseSpecialistAgent):
    name = "account_kyc"
    description = "Handles account management, KYC verification, identity documents, and account status"
    system_prompt_template = """You are the Account & KYC Support Agent for {firm_name}.

Your role is to help traders with:
- Account creation and setup
- KYC document submission and verification status
- Password resets and login issues
- Account upgrades and modifications
- Linking trading platform accounts
- Account closure requests

Rules:
- Verify trader identity before making account changes
- Never share KYC documents or sensitive personal data
- Guide traders through the KYC process step by step
- Escalate account closure requests to compliance

{firm_specific_rules}"""

    knowledge_scope = ["kyc_requirements", "account_management", "platform_guides"]
    risk_level = "medium"

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "get_kyc_status", "description": "Check KYC verification status"},
            {"name": "initiate_kyc_verification", "description": "Start KYC verification process"},
            {"name": "get_account_details", "description": "Get trader account details"},
            {"name": "reset_trading_account", "description": "Reset a trading account"},
            {"name": "upgrade_account", "description": "Upgrade account tier"},
            {"name": "link_trading_account", "description": "Link a trading platform account"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(
            firm_name="Trading Firm",
            firm_specific_rules="",
        )
