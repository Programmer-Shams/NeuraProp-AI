"""Tool executor — validates, authorizes, and executes tool calls with audit logging."""

import hashlib
import json
import time
import uuid
from typing import Any

from neuraprop_core.logging import get_logger

from agents.tools.base import BaseTool, ToolContext, ToolResult
from agents.tools.registry import get_tool_registry

logger = get_logger(__name__)

# Risk levels that require human approval before execution
APPROVAL_REQUIRED_RISK = {"critical"}

# In-memory idempotency cache (replace with Redis in production)
_idempotency_cache: dict[str, ToolResult] = {}


def _compute_idempotency_key(tool: BaseTool, params: dict, context: ToolContext) -> str | None:
    """Compute a cache key for idempotent tool calls."""
    if not tool.idempotency_key_fields:
        return None

    key_parts = [tool.name, context.firm_id]
    for field in tool.idempotency_key_fields:
        key_parts.append(str(params.get(field, "")))

    raw = ":".join(key_parts)
    return hashlib.sha256(raw.encode()).hexdigest()


async def execute_tool(
    tool_name: str,
    params: dict[str, Any],
    context: ToolContext,
) -> ToolResult:
    """
    Execute a tool call through the full pipeline:

    1. Lookup tool in registry
    2. Validate parameters via JSON Schema
    3. Check idempotency cache
    4. Risk assessment (auto-approve or queue for human)
    5. Execute the tool
    6. Audit log the result
    7. Cache idempotent results
    """
    execution_id = str(uuid.uuid4())[:8]
    start_time = time.monotonic()

    registry = get_tool_registry()
    tool = registry.get(tool_name)

    if tool is None:
        logger.warning("tool_not_found", tool=tool_name)
        return ToolResult(success=False, error=f"Unknown tool: {tool_name}")

    logger.info(
        "tool_execution_start",
        execution_id=execution_id,
        tool=tool_name,
        agent=context.agent_name,
        firm_id=context.firm_id,
        risk=tool.risk_level,
    )

    # Check idempotency
    idempotency_key = _compute_idempotency_key(tool, params, context)
    if idempotency_key and idempotency_key in _idempotency_cache:
        logger.info("tool_idempotent_hit", tool=tool_name, key=idempotency_key[:12])
        return _idempotency_cache[idempotency_key]

    # Risk check — critical actions need human approval
    if tool.risk_level in APPROVAL_REQUIRED_RISK or tool.requires_approval:
        logger.info("tool_requires_approval", tool=tool_name, risk=tool.risk_level)
        return ToolResult(
            success=False,
            error="This action requires human approval. It has been queued for review.",
            data={"pending_approval": True, "execution_id": execution_id},
        )

    # Validate parameters
    try:
        is_valid = await tool.validate(params, context)
        if not is_valid:
            return ToolResult(success=False, error=f"Validation failed for {tool_name}")
    except Exception as e:
        logger.exception("tool_validation_error", tool=tool_name)
        return ToolResult(success=False, error=f"Validation error: {e}")

    # Execute
    try:
        result = await tool.execute(params, context)
    except Exception as e:
        logger.exception("tool_execution_error", tool=tool_name)
        result = ToolResult(success=False, error=f"Execution error: {e}")

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    logger.info(
        "tool_execution_complete",
        execution_id=execution_id,
        tool=tool_name,
        success=result.success,
        elapsed_ms=elapsed_ms,
    )

    # Cache idempotent successful results
    if idempotency_key and result.success:
        _idempotency_cache[idempotency_key] = result

    return result


async def execute_tool_calls(
    tool_calls: list[dict[str, Any]],
    context: ToolContext,
) -> list[dict[str, Any]]:
    """Execute a batch of tool calls from an LLM response.

    Each tool_call dict has: {id, function: {name, arguments}}
    Returns list of results suitable for feeding back to the LLM.
    """
    results = []
    for call in tool_calls:
        func = call.get("function", {})
        tool_name = func.get("name", "")

        try:
            params = json.loads(func.get("arguments", "{}"))
        except json.JSONDecodeError:
            params = {}

        result = await execute_tool(tool_name, params, context)

        results.append({
            "tool_call_id": call.get("id", ""),
            "role": "tool",
            "content": json.dumps(result.data if result.success else {"error": result.error}),
        })

    return results
