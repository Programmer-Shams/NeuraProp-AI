"""Compliance specialist agent — always escalates actions to human review."""

from typing import Any
from agents.specialists.base import BaseSpecialistAgent


class ComplianceAgent(BaseSpecialistAgent):
    name = "compliance"
    description = "Handles regulatory questions, compliance issues, trading restrictions"
    system_prompt_template = """You are the Compliance Support Agent for {firm_name}.

Provide information about compliance policies and regulatory requirements.
IMPORTANT: Never make binding compliance decisions. Always escalate action items to human review.

{firm_specific_rules}"""

    knowledge_scope = ["regulatory_docs", "compliance_policies", "restricted_jurisdictions"]
    risk_level = "critical"

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "get_compliance_status", "description": "Get trader's compliance status"},
            {"name": "flag_compliance_issue", "description": "Flag an issue for compliance review"},
            {"name": "check_trading_restrictions", "description": "Check jurisdiction-based restrictions"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
