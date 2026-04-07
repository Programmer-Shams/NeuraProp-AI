"""Tool registry — discovers, validates, and dispatches tool calls."""

from typing import Any

from neuraprop_core.logging import get_logger

from agents.tools.base import BaseTool, ToolContext, ToolResult

logger = get_logger(__name__)


class ToolRegistry:
    """Central registry for all agent tools.

    Each specialist agent registers its tools at startup. The registry handles
    lookup, validation, and dispatching tool calls to the correct implementation.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            logger.warning("tool_already_registered", tool=tool.name)
        self._tools[tool.name] = tool
        logger.debug("tool_registered", tool=tool.name, risk=tool.risk_level)

    def register_many(self, tools: list[BaseTool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_for_agent(self, agent_name: str) -> list[BaseTool]:
        """Return tools that belong to a specific agent (by name prefix convention)."""
        prefix = f"{agent_name}_" if not agent_name.endswith("_") else agent_name
        return [t for t in self._tools.values() if t.name.startswith(prefix)]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def to_openai_schema(self, tool_names: list[str] | None = None) -> list[dict[str, Any]]:
        """Convert tools to OpenAI function-calling schema for LLM consumption."""
        tools = self._tools.values()
        if tool_names:
            tools = [t for t in tools if t.name in tool_names]

        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]


# Global registry singleton
_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
