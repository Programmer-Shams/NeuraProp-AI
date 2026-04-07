"""Technical support specialist agent."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.technical_tools import get_technical_tools


class TechnicalAgent(BaseSpecialistAgent):
    name = "technical"
    description = "Handles platform issues, login problems, order execution, data feed issues"
    system_prompt_template = """You are the Technical Support Agent for {firm_name}.

Help traders with platform issues, connectivity problems, trade execution concerns,
and technical setup. Diagnose issues systematically before suggesting solutions.

{firm_specific_rules}"""

    knowledge_scope = ["platform_guides", "known_issues", "setup_tutorials"]
    risk_level = "low"
    max_tool_calls = 4

    def get_tool_instances(self) -> list[BaseTool]:
        return get_technical_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
