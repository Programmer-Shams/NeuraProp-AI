"""Technical support specialist agent."""

from typing import Any
from agents.specialists.base import BaseSpecialistAgent


class TechnicalAgent(BaseSpecialistAgent):
    name = "technical"
    description = "Handles platform issues, login problems, order execution, data feed issues"
    system_prompt_template = """You are the Technical Support Agent for {firm_name}.

Help traders with platform issues, connectivity problems, trade execution concerns,
and technical setup. Diagnose issues systematically before suggesting solutions.

{firm_specific_rules}"""

    knowledge_scope = ["platform_guides", "known_issues", "setup_tutorials"]
    risk_level = "low"

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "check_platform_status", "description": "Check trading platform status"},
            {"name": "check_trade_execution", "description": "Verify trade execution details"},
            {"name": "verify_platform_credentials", "description": "Verify platform login credentials"},
            {"name": "submit_technical_ticket", "description": "Submit a technical investigation ticket"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
