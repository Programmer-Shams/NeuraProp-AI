"""Onboarding/Welcome specialist agent."""

from typing import Any
from agents.specialists.base import BaseSpecialistAgent


class OnboardingAgent(BaseSpecialistAgent):
    name = "onboarding"
    description = "Helps new traders get started, choose challenges, set up platforms"
    system_prompt_template = """You are the Onboarding Agent for {firm_name}.

Welcome new traders and help them get started. Guide them through challenge selection,
platform setup, and answer getting-started questions with enthusiasm and clarity.

{firm_specific_rules}"""

    knowledge_scope = ["getting_started", "platform_setup", "challenge_overview"]
    risk_level = "medium"

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "get_available_challenges", "description": "List available challenge types"},
            {"name": "create_challenge_account", "description": "Create a new challenge account"},
            {"name": "send_welcome_email", "description": "Send welcome email with setup instructions"},
            {"name": "generate_platform_credentials", "description": "Generate trading platform credentials"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(firm_name="Trading Firm", firm_specific_rules="")
