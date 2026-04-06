"""Base specialist agent class — all specialists inherit from this."""

from abc import ABC, abstractmethod
from typing import Any

from neuraprop_core.logging import get_logger

logger = get_logger(__name__)


class BaseSpecialistAgent(ABC):
    """Base class for all specialist agents."""

    name: str
    description: str
    system_prompt_template: str
    knowledge_scope: list[str]
    max_tool_calls: int = 5
    risk_level: str = "medium"
    escalation_triggers: list[str] = []

    @abstractmethod
    async def get_tools(self, firm_id: str) -> list[dict[str, Any]]:
        """Return available tools for this agent, scoped to the firm."""
        ...

    @abstractmethod
    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        """Build the firm-specific system prompt for this agent."""
        ...

    async def execute(
        self,
        messages: list[dict[str, str]],
        firm_id: str,
        trader_profile: dict | None = None,
        retrieved_knowledge: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the specialist agent.

        Returns dict with 'response', 'tool_calls', 'needs_escalation'.
        """
        system_prompt = await self.build_system_prompt(firm_id, trader_profile)

        # Add retrieved knowledge to context
        if retrieved_knowledge:
            knowledge_text = "\n\n".join(
                f"[Source: {k.get('source', 'unknown')}]\n{k.get('content', '')}"
                for k in retrieved_knowledge
            )
            system_prompt += f"\n\n## Relevant Knowledge Base:\n{knowledge_text}"

        logger.info(
            "specialist_executing",
            agent=self.name,
            firm_id=firm_id,
            message_count=len(messages),
        )

        # TODO: Implement full LLM call with tool use in Phase 2
        # For now, return a structured placeholder
        return {
            "response": f"[{self.name}] Processing your request...",
            "tool_calls": [],
            "needs_escalation": False,
        }
