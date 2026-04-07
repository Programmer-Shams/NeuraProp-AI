"""Graph nodes for the orchestrator — each node transforms the conversation state."""

from typing import Any

from neuraprop_core.logging import get_logger

from agents.orchestrator.state import ConversationState
from agents.llm.router import llm_classify_intent
from agents.specialists.payout import PayoutAgent
from agents.specialists.rules import RulesAgent
from agents.specialists.account_kyc import AccountKYCAgent
from agents.specialists.technical import TechnicalAgent
from agents.specialists.billing import BillingAgent
from agents.specialists.compliance import ComplianceAgent
from agents.specialists.onboarding import OnboardingAgent
from agents.tools.registry import get_tool_registry

logger = get_logger(__name__)

# Intent → specialist agent mapping
INTENT_TO_AGENT = {
    "payout_withdrawal": "payout",
    "rules_challenge": "rules",
    "account_kyc": "account_kyc",
    "technical_support": "technical",
    "billing_refund": "billing",
    "compliance": "compliance",
    "onboarding": "onboarding",
    "general_inquiry": "orchestrator",
}

# Specialist agent instances
SPECIALISTS = {
    "payout": PayoutAgent(),
    "rules": RulesAgent(),
    "account_kyc": AccountKYCAgent(),
    "technical": TechnicalAgent(),
    "billing": BillingAgent(),
    "compliance": ComplianceAgent(),
    "onboarding": OnboardingAgent(),
}

# Register all specialist tools at import time
_tools_registered = False


def _ensure_tools_registered() -> None:
    global _tools_registered
    if _tools_registered:
        return
    for agent in SPECIALISTS.values():
        agent.register_tools()
    _tools_registered = True
    registry = get_tool_registry()
    logger.info("all_tools_registered", count=len(registry.list_tools()))


async def load_context(state: ConversationState) -> dict[str, Any]:
    """
    Load trader profile, conversation history, and firm config from DB.
    """
    _ensure_tools_registered()

    logger.info(
        "loading_context",
        firm_id=state["firm_id"],
        trader_id=state.get("trader_id"),
    )

    # TODO: Replace with actual DB queries
    # - Load trader profile from traders table
    # - Load recent conversation history from messages table
    # - Load firm config from firm_configs table
    return {
        "trader_profile": state.get("trader_profile") or {},
        "trader_accounts": state.get("trader_accounts") or [],
    }


async def classify_intent(state: ConversationState) -> dict[str, Any]:
    """
    Classify the trader's intent using a fast LLM call.
    Uses Claude Haiku or GPT-4o-mini for speed and cost.
    """
    # Get the latest user message
    user_messages = [m for m in state["messages"] if hasattr(m, "content")]
    if user_messages:
        latest_content = user_messages[-1].content
    else:
        # Fallback for dict-style messages
        dict_messages = [m for m in state["messages"] if isinstance(m, dict) and m.get("role") == "user"]
        latest_content = dict_messages[-1]["content"] if dict_messages else ""

    logger.info("classifying_intent", content_preview=latest_content[:100])

    try:
        classification = await llm_classify_intent(
            message=latest_content,
            trader_profile=state.get("trader_profile"),
            firm_id=state["firm_id"],
        )
        target_agent = INTENT_TO_AGENT.get(classification.intent, "orchestrator")

        logger.info(
            "intent_classified",
            intent=classification.intent,
            confidence=classification.confidence,
            target_agent=target_agent,
            reasoning=classification.reasoning,
        )

        return {
            "classified_intent": classification.intent,
            "confidence": classification.confidence,
            "current_agent": target_agent,
        }

    except Exception:
        logger.exception("intent_classification_failed")
        return {
            "classified_intent": "general_inquiry",
            "confidence": 0.5,
            "current_agent": "orchestrator",
        }


async def handle_specialist(state: ConversationState) -> dict[str, Any]:
    """
    Execute the specialist agent with real LLM calls and tool use.
    """
    agent_name = state.get("current_agent", "orchestrator")
    intent = state.get("classified_intent", "general_inquiry")

    logger.info("specialist_handling", agent=agent_name, intent=intent)

    specialist = SPECIALISTS.get(agent_name)

    if not specialist:
        # Fallback for orchestrator/unknown — give a generic helpful response
        return {
            "final_response": (
                "Thank you for reaching out! I'd be happy to help you. "
                "Could you provide a bit more detail about what you need assistance with? "
                "I can help with payouts, trading rules, account management, technical issues, "
                "billing, compliance, or getting started."
            ),
            "response_ready": True,
        }

    # Convert state messages to the format specialists expect
    messages = []
    for m in state["messages"]:
        if hasattr(m, "content"):
            messages.append({"role": getattr(m, "type", "user"), "content": m.content})
        elif isinstance(m, dict):
            messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

    try:
        result = await specialist.execute(
            messages=messages,
            firm_id=state["firm_id"],
            trader_id=state.get("trader_id"),
            trader_profile=state.get("trader_profile"),
            retrieved_knowledge=state.get("retrieved_knowledge"),
        )

        update: dict[str, Any] = {
            "final_response": result["response"],
            "response_ready": True,
            "tool_results": result.get("tool_calls", []),
        }

        if result.get("needs_escalation"):
            update["needs_escalation"] = True
            update["escalation_reason"] = f"Escalation triggered by {agent_name} agent"

        return update

    except Exception:
        logger.exception("specialist_execution_failed", agent=agent_name)
        return {
            "final_response": (
                "I apologize, but I'm experiencing a temporary issue processing your request. "
                "Let me connect you with our support team for immediate assistance."
            ),
            "needs_escalation": True,
            "escalation_reason": f"Specialist {agent_name} failed",
            "response_ready": True,
        }


async def post_process(state: ConversationState) -> dict[str, Any]:
    """
    Post-process the response before sending.
    - Save conversation state to DB
    - Log analytics events
    - Format response for channel
    """
    logger.info(
        "post_processing",
        conversation_id=state["conversation_id"],
        agent=state.get("current_agent"),
    )

    # TODO: Persist to database, log analytics
    return {}


async def escalate(state: ConversationState) -> dict[str, Any]:
    """
    Escalate the conversation to human support.
    Creates a ticket and notifies the firm's support team.
    """
    reason = state.get("escalation_reason", "Low confidence or explicit escalation request")
    logger.info(
        "escalating_conversation",
        conversation_id=state["conversation_id"],
        reason=reason,
    )

    # TODO: Create ticket in database, send notification

    return {
        "needs_escalation": True,
        "escalation_reason": reason,
        "final_response": (
            "I'm connecting you with our support team for further assistance. "
            "A team member will review your case shortly. "
            "Thank you for your patience."
        ),
        "response_ready": True,
    }
