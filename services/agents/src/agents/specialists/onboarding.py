"""Onboarding/Welcome specialist agent."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.onboarding_tools import get_onboarding_tools


class OnboardingAgent(BaseSpecialistAgent):
    name = "onboarding"
    description = "Helps new traders get started, choose challenges, set up platforms"
    system_prompt_template = """You are the Onboarding Agent for {firm_name}.

Welcome new traders and help them get started. Guide them through challenge selection,
platform setup, and answer getting-started questions with enthusiasm and clarity.

{firm_specific_rules}"""

    knowledge_scope = ["getting_started", "platform_setup", "challenge_overview"]
    risk_level = "medium"
    max_tool_calls = 4

    def get_tool_instances(self) -> list[BaseTool]:
        return get_onboarding_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
