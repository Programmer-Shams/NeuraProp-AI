"""Base specialist agent class — all specialists inherit from this."""

from abc import ABC, abstractmethod
from typing import Any

from neuraprop_core.logging import get_logger

from agents.llm.agent_caller import run_agent_loop
from agents.tools.base import BaseTool, ToolContext
from agents.tools.registry import get_tool_registry

logger = get_logger(__name__)


class BaseSpecialistAgent(ABC):
    """Base class for all specialist agents.

    Each specialist defines its own system prompt, tools, and configuration.
    The execute() method runs a multi-turn LLM loop with tool calling.
    """

    name: str
    description: str
    system_prompt_template: str
    knowledge_scope: list[str]
    max_tool_calls: int = 5
    risk_level: str = "medium"
    escalation_triggers: list[str] = []

    @abstractmethod
    def get_tool_instances(self) -> list[BaseTool]:
        """Return tool class instances for this agent."""
        ...

    @abstractmethod
    async def build_system_prompt(self, firm_id: str, trader_profile: dict | None = None) -> str:
        """Build the firm-specific system prompt for this agent."""
        ...

    def register_tools(self) -> None:
        """Register this agent's tools in the global registry."""
        registry = get_tool_registry()
        registry.register_many(self.get_tool_instances())

    def get_tool_names(self) -> list[str]:
        """Return names of tools this agent uses."""
        return [t.name for t in self.get_tool_instances()]

    async def execute(
        self,
        messages: list[dict[str, str]],
        firm_id: str,
        trader_id: str | None = None,
        trader_profile: dict | None = None,
        retrieved_knowledge: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the specialist agent with real LLM calls and tool use.

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

        # Add trader profile context
        if trader_profile:
            profile_summary = (
                f"\n\n## Trader Profile:\n"
                f"- Name: {trader_profile.get('display_name', 'Unknown')}\n"
                f"- Email: {trader_profile.get('email', 'Unknown')}\n"
                f"- KYC Status: {trader_profile.get('kyc_status', 'Unknown')}\n"
                f"- Risk Tier: {trader_profile.get('risk_tier', 'standard')}\n"
            )
            system_prompt += profile_summary

        # Prepare tool schemas for LLM
        registry = get_tool_registry()
        tool_schemas = registry.to_openai_schema(self.get_tool_names())

        # Prepare tool context
        tool_context = ToolContext(
            firm_id=firm_id,
            trader_id=trader_id,
            agent_name=self.name,
        )

        logger.info(
            "specialist_executing",
            agent=self.name,
            firm_id=firm_id,
            message_count=len(messages),
            tools_available=len(tool_schemas),
        )

        # Run the agent loop
        result = await run_agent_loop(
            system_prompt=system_prompt,
            messages=messages,
            tools=tool_schemas,
            tool_context=tool_context,
            max_iterations=self.max_tool_calls,
        )

        # Check for escalation triggers in the response
        needs_escalation = False
        response_lower = result["response"].lower()
        for trigger in self.escalation_triggers:
            if trigger.lower() in response_lower:
                needs_escalation = True
                break

        logger.info(
            "specialist_completed",
            agent=self.name,
            iterations=result["iterations"],
            tool_calls=len(result["tool_calls_made"]),
            needs_escalation=needs_escalation,
        )

        return {
            "response": result["response"],
            "tool_calls": result["tool_calls_made"],
            "needs_escalation": needs_escalation,
        }
