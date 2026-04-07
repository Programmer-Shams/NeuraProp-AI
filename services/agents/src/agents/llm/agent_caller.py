"""Agent LLM caller — handles multi-turn tool-use conversations with specialists."""

import json
from typing import Any

import litellm

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger

from agents.llm.router import MODELS
from agents.tools.base import ToolContext
from agents.tools.executor import execute_tool

logger = get_logger(__name__)


async def run_agent_loop(
    system_prompt: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    tool_context: ToolContext,
    max_iterations: int = 5,
    task_type: str = "agent_reasoning",
) -> dict[str, Any]:
    """
    Run a multi-turn LLM agent loop with tool calling.

    The loop:
    1. Send messages + tools to LLM
    2. If LLM returns tool calls, execute them
    3. Append tool results to messages
    4. Repeat until LLM returns a text response or max_iterations reached

    Returns: {response: str, tool_calls_made: list, iterations: int}
    """
    settings = get_settings()
    models = MODELS.get(task_type, MODELS["agent_reasoning"])
    model = models["primary"]
    api_key = (
        settings.anthropic_api_key if "claude" in model else settings.openai_api_key
    )

    all_messages = [{"role": "system", "content": system_prompt}] + messages
    tool_calls_made: list[dict[str, Any]] = []

    for iteration in range(max_iterations):
        try:
            response = await litellm.acompletion(
                model=model,
                messages=all_messages,
                tools=tools if tools else None,
                temperature=0.1,
                max_tokens=2048,
                api_key=api_key,
            )
        except Exception:
            logger.exception("agent_llm_call_failed", model=model, iteration=iteration)
            # Try fallback
            fallback = models.get("fallback")
            if fallback:
                fallback_key = (
                    settings.anthropic_api_key if "claude" in fallback else settings.openai_api_key
                )
                response = await litellm.acompletion(
                    model=fallback,
                    messages=all_messages,
                    tools=tools if tools else None,
                    temperature=0.1,
                    max_tokens=2048,
                    api_key=fallback_key,
                )
            else:
                raise

        choice = response.choices[0]
        message = choice.message

        logger.info(
            "agent_loop_iteration",
            iteration=iteration,
            model=model,
            has_tool_calls=bool(message.tool_calls),
            tokens_in=response.usage.prompt_tokens if response.usage else 0,
            tokens_out=response.usage.completion_tokens if response.usage else 0,
        )

        # No tool calls — LLM has a final text response
        if not message.tool_calls:
            return {
                "response": message.content or "",
                "tool_calls_made": tool_calls_made,
                "iterations": iteration + 1,
            }

        # Process tool calls
        # Add the assistant message with tool calls to context
        all_messages.append(message.model_dump())

        for tool_call in message.tool_calls:
            func = tool_call.function
            tool_name = func.name

            try:
                params = json.loads(func.arguments) if func.arguments else {}
            except json.JSONDecodeError:
                params = {}

            logger.info("agent_tool_call", tool=tool_name, params=list(params.keys()))

            result = await execute_tool(tool_name, params, tool_context)

            tool_calls_made.append({
                "tool": tool_name,
                "params": params,
                "success": result.success,
                "data": result.data if result.success else {"error": result.error},
            })

            # Add tool result to messages
            all_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result.data if result.success else {"error": result.error}),
            })

    # Max iterations reached — return whatever we have
    logger.warning("agent_loop_max_iterations", iterations=max_iterations)
    return {
        "response": "I've been working on your request but need more steps to complete it. Let me summarize what I've found so far.",
        "tool_calls_made": tool_calls_made,
        "iterations": max_iterations,
    }
