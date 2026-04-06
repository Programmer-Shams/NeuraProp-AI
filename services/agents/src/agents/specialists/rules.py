"""Rules/Challenge specialist agent — answers questions about trading rules and evaluations."""

from typing import Any

from agents.specialists.base import BaseSpecialistAgent


class RulesAgent(BaseSpecialistAgent):
    name = "rules"
    description = "Handles questions about challenge rules, evaluation criteria, drawdown limits, and phase progression"
    system_prompt_template = """You are the Rules & Challenge Support Agent for {firm_name}.

Your role is to help traders with:
- Explaining challenge rules and requirements
- Clarifying profit targets and drawdown limits
- Answering questions about phase progression
- Explaining consistency rules and trading restrictions
- Providing information about scaling plans
- Addressing rule violation inquiries

Rules:
- Always provide accurate rule information from the knowledge base
- If a rule is ambiguous, acknowledge it and provide the most common interpretation
- Never make promises about rule exceptions
- Refer traders to the compliance team for disputed violations

{firm_specific_rules}"""

    knowledge_scope = ["challenge_rules", "evaluation_criteria", "trading_restrictions"]
    risk_level = "low"
    max_tool_calls = 3

    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        return [
            {"name": "get_challenge_rules", "description": "Get current challenge rules and parameters"},
            {"name": "get_trader_challenge_status", "description": "Get trader's current challenge progress"},
            {"name": "get_rule_violation_history", "description": "Get trader's rule violation history"},
            {"name": "check_specific_rule", "description": "Look up a specific trading rule"},
        ]

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(
            firm_name="Trading Firm",
            firm_specific_rules="",
        )
