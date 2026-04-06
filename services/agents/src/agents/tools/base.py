"""Base tool class and execution context."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolContext:
    """Context provided to every tool execution."""

    firm_id: str
    trader_id: str | None = None
    conversation_id: str | None = None
    agent_name: str = ""


@dataclass
class ToolResult:
    """Standard result from tool execution."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseTool(ABC):
    """Base class for all agent tools."""

    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
    required_permissions: list[str] = []
    risk_level: str = "low"
    requires_approval: bool = False
    idempotency_key_fields: list[str] = []

    @abstractmethod
    async def validate(self, params: dict, context: ToolContext) -> bool:
        """Pre-execution validation."""
        ...

    @abstractmethod
    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        """Execute the tool action."""
        ...
