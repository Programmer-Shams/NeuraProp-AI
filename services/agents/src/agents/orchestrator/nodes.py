"""Graph nodes for the orchestrator — each node transforms the conversation state."""

from typing import Any

from neuraprop_core.logging import get_logger

from agents.orchestrator.state import ConversationState, IntentClassification
from agents.llm.router import llm_classify_intent

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


async def load_context(state: ConversationState) -> dict[str, Any]:
    """
    Load trader profile, conversation history, and firm config from DB.

    TODO: Wire to actual database queries in Phase 2.
    """
    logger.info(
        "loading_context",
        firm_id=state["firm_id"],
        trader_id=state.get("trader_id"),
    )

    # Placeholder — will be replaced with actual DB lookups
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
    latest_content = user_messages[-1].content if user_messages else ""

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


async def route_to_specialist(state: ConversationState) -> dict[str, Any]:
    """Route to the appropriate specialist agent based on classified intent."""
    agent = state.get("current_agent", "orchestrator")
    previous = list(state.get("previous_agents", []))
    previous.append(agent)

    return {
        "current_agent": agent,
        "previous_agents": previous,
    }


async def handle_specialist(state: ConversationState) -> dict[str, Any]:
    """
    Execute the specialist agent.

    TODO: Wire to actual specialist agent implementations in Phase 2.
    Currently returns a placeholder response.
    """
    agent_name = state.get("current_agent", "orchestrator")
    intent = state.get("classified_intent", "general_inquiry")

    logger.info(
        "specialist_handling",
        agent=agent_name,
        intent=intent,
    )

    # Placeholder response — will be replaced with actual specialist logic
    response = (
        f"Thank you for reaching out. I understand your inquiry is about "
        f"'{intent.replace('_', ' ')}'. I'm the {agent_name} agent and I'm "
        f"working on getting you the information you need. "
        f"This is a placeholder response — full agent logic coming in Phase 2."
    )

    return {
        "final_response": response,
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
