"""Account/KYC specialist agent."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.account_tools import get_account_tools


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
    escalation_triggers = ["close account", "delete data", "gdpr"]

    def get_tool_instances(self) -> list[BaseTool]:
        return get_account_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(
            firm_name="Trading Firm",
            firm_specific_rules="",
        )
