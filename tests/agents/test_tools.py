"""Tests for agent tools — registry, executor, and tool implementations."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from agents.tools.base import BaseTool, ToolContext, ToolResult
from agents.tools.registry import ToolRegistry


# --- Test Tool Implementations ---

class MockTool(BaseTool):
    name = "mock_tool"
    description = "A mock tool for testing"
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string"},
        },
        "required": ["input"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return "input" in params

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={"output": f"processed: {params['input']}"})


class CriticalTool(BaseTool):
    name = "critical_action"
    description = "A high-risk tool"
    parameters = {"type": "object", "properties": {}}
    risk_level = "critical"
    requires_approval = True

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return True

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={"done": True})


class IdempotentTool(BaseTool):
    name = "idempotent_check"
    description = "An idempotent tool"
    parameters = {
        "type": "object",
        "properties": {"account_id": {"type": "string"}},
    }
    risk_level = "low"
    idempotency_key_fields = ["account_id"]

    call_count = 0

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return True

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        IdempotentTool.call_count += 1
        return ToolResult(success=True, data={"balance": 5000})


# --- Registry Tests ---

class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()
        tool = MockTool()
        registry.register(tool)
        assert registry.get("mock_tool") is tool

    def test_get_nonexistent_returns_none(self):
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_register_many(self):
        registry = ToolRegistry()
        tools = [MockTool(), CriticalTool()]
        registry.register_many(tools)
        assert len(registry.list_tools()) == 2

    def test_list_tools(self):
        registry = ToolRegistry()
        registry.register(MockTool())
        registry.register(CriticalTool())
        names = registry.list_tools()
        assert "mock_tool" in names
        assert "critical_action" in names

    def test_to_openai_schema(self):
        registry = ToolRegistry()
        registry.register(MockTool())
        schema = registry.to_openai_schema()
        assert len(schema) == 1
        assert schema[0]["type"] == "function"
        assert schema[0]["function"]["name"] == "mock_tool"
        assert "parameters" in schema[0]["function"]

    def test_to_openai_schema_filtered(self):
        registry = ToolRegistry()
        registry.register(MockTool())
        registry.register(CriticalTool())
        schema = registry.to_openai_schema(tool_names=["mock_tool"])
        assert len(schema) == 1
        assert schema[0]["function"]["name"] == "mock_tool"


# --- Executor Tests ---

class TestToolExecution:
    @pytest.mark.asyncio
    async def test_execute_basic_tool(self):
        from agents.tools.executor import execute_tool
        from agents.tools.registry import get_tool_registry

        # Reset global registry
        import agents.tools.registry as reg_mod
        reg_mod._registry = None
        registry = get_tool_registry()
        registry.register(MockTool())

        ctx = ToolContext(firm_id="firm-1", agent_name="test")
        result = await execute_tool("mock_tool", {"input": "hello"}, ctx)
        assert result.success is True
        assert result.data["output"] == "processed: hello"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        from agents.tools.executor import execute_tool

        import agents.tools.registry as reg_mod
        reg_mod._registry = None

        ctx = ToolContext(firm_id="firm-1", agent_name="test")
        result = await execute_tool("nonexistent", {}, ctx)
        assert result.success is False
        assert "Unknown tool" in result.error

    @pytest.mark.asyncio
    async def test_critical_tool_requires_approval(self):
        from agents.tools.executor import execute_tool
        from agents.tools.registry import get_tool_registry

        import agents.tools.registry as reg_mod
        reg_mod._registry = None
        registry = get_tool_registry()
        registry.register(CriticalTool())

        ctx = ToolContext(firm_id="firm-1", agent_name="test")
        result = await execute_tool("critical_action", {}, ctx)
        assert result.success is False
        assert "approval" in result.error.lower()
        assert result.data.get("pending_approval") is True

    @pytest.mark.asyncio
    async def test_idempotent_tool_cached(self):
        from agents.tools.executor import execute_tool, _idempotency_cache
        from agents.tools.registry import get_tool_registry

        import agents.tools.registry as reg_mod
        reg_mod._registry = None
        _idempotency_cache.clear()
        IdempotentTool.call_count = 0

        registry = get_tool_registry()
        registry.register(IdempotentTool())

        ctx = ToolContext(firm_id="firm-1", agent_name="test")
        params = {"account_id": "ACC-123"}

        # First call
        r1 = await execute_tool("idempotent_check", params, ctx)
        assert r1.success is True
        assert IdempotentTool.call_count == 1

        # Second call with same params — should be cached
        r2 = await execute_tool("idempotent_check", params, ctx)
        assert r2.success is True
        assert IdempotentTool.call_count == 1  # Not incremented

    @pytest.mark.asyncio
    async def test_execute_tool_calls_batch(self):
        from agents.tools.executor import execute_tool_calls
        from agents.tools.registry import get_tool_registry

        import agents.tools.registry as reg_mod
        reg_mod._registry = None
        registry = get_tool_registry()
        registry.register(MockTool())

        ctx = ToolContext(firm_id="firm-1", agent_name="test")
        tool_calls = [
            {
                "id": "call_1",
                "function": {
                    "name": "mock_tool",
                    "arguments": json.dumps({"input": "test1"}),
                },
            },
            {
                "id": "call_2",
                "function": {
                    "name": "mock_tool",
                    "arguments": json.dumps({"input": "test2"}),
                },
            },
        ]

        results = await execute_tool_calls(tool_calls, ctx)
        assert len(results) == 2
        assert results[0]["tool_call_id"] == "call_1"
        assert results[0]["role"] == "tool"
        r1_data = json.loads(results[0]["content"])
        assert r1_data["output"] == "processed: test1"


# --- ToolContext Tests ---

class TestToolContext:
    def test_defaults(self):
        ctx = ToolContext(firm_id="firm-1")
        assert ctx.firm_id == "firm-1"
        assert ctx.trader_id is None
        assert ctx.conversation_id is None
        assert ctx.agent_name == ""

    def test_full_context(self):
        ctx = ToolContext(
            firm_id="firm-1",
            trader_id="trader-1",
            conversation_id="conv-1",
            agent_name="payout",
        )
        assert ctx.trader_id == "trader-1"
        assert ctx.agent_name == "payout"


class TestToolResult:
    def test_success_result(self):
        result = ToolResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data["key"] == "value"
        assert result.error is None

    def test_failure_result(self):
        result = ToolResult(success=False, error="something failed")
        assert result.success is False
        assert result.error == "something failed"
        assert result.data == {}
