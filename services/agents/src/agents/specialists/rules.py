"""Rules/Challenge specialist agent — answers questions about trading rules and evaluations."""

from agents.specialists.base import BaseSpecialistAgent
from agents.tools.base import BaseTool
from agents.tools.rules_tools import get_rules_tools


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
    max_tool_calls = 4
    escalation_triggers = ["dispute", "unfair", "lawsuit"]

    def get_tool_instances(self) -> list[BaseTool]:
        return get_rules_tools()

    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        return self.system_prompt_template.format(
            firm_name="Trading Firm",
            firm_specific_rules="",
        )
