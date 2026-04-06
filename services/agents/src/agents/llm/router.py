"""LLM Router — routes different tasks to optimal models via LiteLLM."""

import json
from typing import Any

import litellm

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger

from agents.orchestrator.state import IntentClassification

logger = get_logger(__name__)

# Disable LiteLLM telemetry
litellm.telemetry = False

# Model routing table
MODELS = {
    "intent_classification": {
        "primary": "claude-haiku-4-5-20251001",
        "fallback": "gpt-4o-mini",
    },
    "agent_reasoning": {
        "primary": "claude-sonnet-4-6",
        "fallback": "gpt-4o",
    },
    "complex_analysis": {
        "primary": "claude-opus-4-6",
        "fallback": "gpt-4o",
    },
    "embedding": {
        "primary": "text-embedding-3-small",
    },
}


async def llm_call(
    task_type: str,
    messages: list[dict[str, str]],
    response_format: dict | None = None,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> str:
    """
    Make an LLM call with automatic fallback.

    Uses LiteLLM as a library (not proxy) for zero latency overhead.
    """
    settings = get_settings()
    models = MODELS.get(task_type, MODELS["agent_reasoning"])

    for model_key in ["primary", "fallback"]:
        model = models.get(model_key)
        if not model:
            continue

        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                api_key=(
                    settings.anthropic_api_key
                    if "claude" in model
                    else settings.openai_api_key
                ),
            )

            content = response.choices[0].message.content
            logger.info(
                "llm_call_success",
                task_type=task_type,
                model=model,
                tokens_in=response.usage.prompt_tokens if response.usage else 0,
                tokens_out=response.usage.completion_tokens if response.usage else 0,
            )
            return content

        except Exception:
            logger.exception("llm_call_failed", model=model, task_type=task_type)
            if model_key == "fallback":
                raise

    raise RuntimeError(f"All LLM models failed for task: {task_type}")


async def llm_classify_intent(
    message: str,
    trader_profile: dict[str, Any] | None = None,
    firm_id: str | None = None,
) -> IntentClassification:
    """
    Classify the trader's intent using a fast model.

    Returns structured IntentClassification.
    """
    profile_context = ""
    if trader_profile:
        profile_context = f"\nTrader context: {json.dumps(trader_profile, default=str)}"

    system_prompt = f"""You are an intent classifier for a prop trading firm's customer support system.

Classify the trader's message into one of these categories:
- payout_withdrawal: Questions about payouts, withdrawals, payment status, profit splits
- rules_challenge: Questions about trading rules, challenge requirements, evaluation criteria, drawdown limits
- account_kyc: Account management, KYC verification, identity documents, account status
- technical_support: Platform issues, login problems, order execution, data feed issues
- billing_refund: Billing questions, refund requests, subscription management, fee inquiries
- compliance: Regulatory questions, compliance issues, trading restrictions
- onboarding: New trader setup, getting started, platform selection, first challenge
- general_inquiry: General questions that don't fit above categories
- escalate_human: Trader explicitly requests human support, or issue is too sensitive for AI

Respond with a JSON object containing: intent, confidence (0.0-1.0), reasoning, sub_intent (optional).
{profile_context}"""

    response = await llm_call(
        task_type="intent_classification",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        temperature=0.0,
        max_tokens=256,
    )

    try:
        # Parse the JSON response
        data = json.loads(response)
        return IntentClassification(**data)
    except (json.JSONDecodeError, ValueError):
        logger.warning("intent_parse_fallback", raw_response=response[:200])
        return IntentClassification(
            intent="general_inquiry",
            confidence=0.5,
            reasoning="Failed to parse classification response",
        )
