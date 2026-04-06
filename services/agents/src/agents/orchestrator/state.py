"""Conversation state schema for the orchestrator graph."""

from typing import Annotated, Any, Literal

from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class IntentClassification(BaseModel):
    """Structured output from the intent classifier."""

    intent: Literal[
        "payout_withdrawal",
        "rules_challenge",
        "account_kyc",
        "technical_support",
        "billing_refund",
        "compliance",
        "onboarding",
        "general_inquiry",
        "escalate_human",
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    sub_intent: str | None = None


class ConversationState(TypedDict):
    """The state that flows through the orchestrator graph."""

    # Core identifiers
    firm_id: str
    trader_id: str | None
    conversation_id: str
    channel: Literal["discord", "web_chat", "email"]

    # Message history (managed by LangGraph reducer)
    messages: Annotated[list, add_messages]

    # Routing
    classified_intent: str | None
    confidence: float | None
    current_agent: str | None
    previous_agents: list[str]

    # Trader context (loaded from DB)
    trader_profile: dict[str, Any] | None
    trader_accounts: list[dict[str, Any]] | None

    # Agent workspace
    agent_scratchpad: dict[str, Any]
    tool_results: list[dict[str, Any]]
    pending_actions: list[dict[str, Any]]

    # RAG context
    retrieved_knowledge: list[dict[str, Any]]

    # Control flow
    needs_escalation: bool
    escalation_reason: str | None
    response_ready: bool
    final_response: str | None
