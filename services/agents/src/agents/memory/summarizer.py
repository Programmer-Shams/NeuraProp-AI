"""Conversation summarizer — compresses long conversations to fit context windows."""

from neuraprop_core.logging import get_logger

from agents.llm.router import llm_call

logger = get_logger(__name__)

# Summarize when conversation exceeds this many messages
SUMMARIZE_THRESHOLD = 20

SUMMARIZE_PROMPT = """Summarize the following customer support conversation between a trader and an AI agent.
Focus on:
1. What the trader originally asked about
2. Key information gathered (account details, decisions made)
3. Actions taken (tools called, results)
4. Current status of the conversation
5. Any unresolved items

Keep the summary concise (under 200 words) and factual. Do not add opinions or speculation.

Conversation:
{conversation}"""


async def summarize_conversation(messages: list[dict[str, str]]) -> str:
    """
    Summarize a long conversation into a compact context block.

    Uses a fast model (Haiku) to keep costs low — this runs frequently.
    """
    # Format messages for the prompt
    formatted = []
    for m in messages:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        formatted.append(f"{role}: {content}")

    conversation_text = "\n".join(formatted)

    try:
        summary = await llm_call(
            task_type="intent_classification",  # Uses fast model (Haiku)
            messages=[
                {"role": "system", "content": "You are a conversation summarizer. Be concise and factual."},
                {"role": "user", "content": SUMMARIZE_PROMPT.format(conversation=conversation_text)},
            ],
            temperature=0.0,
            max_tokens=512,
        )

        logger.info(
            "conversation_summarized",
            input_messages=len(messages),
            summary_length=len(summary),
        )

        return summary

    except Exception:
        logger.exception("summarization_failed")
        # Fallback: just take the last few messages as-is
        recent = messages[-5:]
        return "\n".join(f"{m.get('role', '?')}: {m.get('content', '')}" for m in recent)


def should_summarize(messages: list[dict]) -> bool:
    """Check if conversation is long enough to warrant summarization."""
    return len(messages) > SUMMARIZE_THRESHOLD


async def compress_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Compress a long message history by summarizing older messages.

    Keeps the most recent messages intact and summarizes the rest.
    Returns a shorter message list with the summary prepended.
    """
    if not should_summarize(messages):
        return messages

    # Keep last 5 messages intact, summarize the rest
    keep_count = 5
    to_summarize = messages[:-keep_count]
    to_keep = messages[-keep_count:]

    summary = await summarize_conversation(to_summarize)

    compressed = [
        {"role": "system", "content": f"[Previous conversation summary]\n{summary}"},
        *to_keep,
    ]

    logger.info(
        "messages_compressed",
        original=len(messages),
        compressed=len(compressed),
    )

    return compressed
