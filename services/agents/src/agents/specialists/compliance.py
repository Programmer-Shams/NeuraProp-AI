"""Compliance specialist agent — always escalates actions to human review."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.compliance_tools import get_compliance_tools


class ComplianceAgent(BaseSpecialistAgent):
    name = "compliance"
    description = "Handles regulatory questions, compliance issues, trading restrictions"
    system_prompt_template = """You are the Compliance Support Agent for {firm_name}.

Provide information about compliance policies and regulatory requirements.
IMPORTANT: Never make binding compliance decisions. Always escalate action items to human review.

{firm_specific_rules}"""

    knowledge_scope = ["regulatory_docs", "compliance_policies", "restricted_jurisdictions"]
    risk_level = "critical"
    max_tool_calls = 3
    escalation_triggers = ["sanction", "aml", "fraud", "legal action"]

    def get_tool_instances(self) -> list[BaseTool]:
        return get_compliance_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
