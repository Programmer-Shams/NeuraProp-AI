"""LangGraph orchestrator graph — the core routing engine."""

from typing import Any

from langgraph.graph import END, StateGraph

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger
from neuraprop_core.sqs import publish_message

from agents.orchestrator.state import ConversationState
from agents.orchestrator.nodes import (
    load_context,
    classify_intent,
    route_to_specialist,
    handle_specialist,
    post_process,
    escalate,
)

logger = get_logger(__name__)


def should_escalate(state: ConversationState) -> str:
    """Decide if we should escalate or route to specialist."""
    if state.get("needs_escalation"):
        return "escalate"

    confidence = state.get("confidence", 0)
    intent = state.get("classified_intent")

    if intent == "escalate_human" or confidence < 0.6:
        return "escalate"

    return "specialist"


def is_response_ready(state: ConversationState) -> str:
    """Check if the specialist has generated a response."""
    if state.get("needs_escalation"):
        return "escalate"
    if state.get("response_ready"):
        return "respond"
    return "respond"


# Build the graph
builder = StateGraph(ConversationState)

# Add nodes
builder.add_node("load_context", load_context)
builder.add_node("classify_intent", classify_intent)
builder.add_node("specialist", handle_specialist)
builder.add_node("post_process", post_process)
builder.add_node("escalate", escalate)

# Define edges
builder.set_entry_point("load_context")
builder.add_edge("load_context", "classify_intent")
builder.add_conditional_edges("classify_intent", should_escalate, {
    "specialist": "specialist",
    "escalate": "escalate",
})
builder.add_conditional_edges("specialist", is_response_ready, {
    "respond": "post_process",
    "escalate": "escalate",
})
builder.add_edge("post_process", END)
builder.add_edge("escalate", END)

# Compile the graph
orchestrator_graph = builder.compile()


async def process_message(unified_message: dict[str, Any]) -> None:
    """
    Process a single inbound message through the orchestrator graph.

    This is the main entry point called by the SQS consumer.
    """
    settings = get_settings()

    # Build initial state from unified message
    initial_state: ConversationState = {
        "firm_id": unified_message["firm_id"],
        "trader_id": unified_message.get("trader_id"),
        "conversation_id": unified_message.get("conversation_id", unified_message["id"]),
        "channel": unified_message["channel"],
        "messages": [
            {"role": "user", "content": unified_message["content"]},
        ],
        "classified_intent": None,
        "confidence": None,
        "current_agent": None,
        "previous_agents": [],
        "trader_profile": None,
        "trader_accounts": None,
        "agent_scratchpad": {},
        "tool_results": [],
        "pending_actions": [],
        "retrieved_knowledge": [],
        "needs_escalation": False,
        "escalation_reason": None,
        "response_ready": False,
        "final_response": None,
    }

    logger.info(
        "orchestrator_processing",
        firm_id=unified_message["firm_id"],
        conversation_id=initial_state["conversation_id"],
        channel=unified_message["channel"],
    )

    # Run the graph
    final_state = await orchestrator_graph.ainvoke(initial_state)

    # Publish response to outbound queue
    if final_state.get("final_response"):
        outbound_message = {
            "conversation_id": final_state["conversation_id"],
            "firm_id": final_state["firm_id"],
            "channel": final_state["channel"],
            "agent_name": final_state.get("current_agent", "orchestrator"),
            "content": final_state["final_response"],
            "metadata": {
                "classified_intent": final_state.get("classified_intent"),
                "confidence": final_state.get("confidence"),
            },
        }
        await publish_message(
            queue_url=settings.sqs_outbound_queue_url,
            message=outbound_message,
        )

    logger.info(
        "orchestrator_completed",
        conversation_id=final_state["conversation_id"],
        agent=final_state.get("current_agent"),
        escalated=final_state.get("needs_escalation", False),
    )
