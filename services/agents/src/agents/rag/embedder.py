"""Embedder — generates vector embeddings using OpenAI's text-embedding-3-small."""

import litellm

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger

logger = get_logger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts.

    Uses OpenAI text-embedding-3-small (1536 dimensions).
    Batches are limited to 2048 texts per call by the API.
    """
    if not texts:
        return []

    settings = get_settings()

    try:
        response = await litellm.aembedding(
            model=EMBEDDING_MODEL,
            input=texts,
            api_key=settings.openai_api_key,
        )

        embeddings = [item["embedding"] for item in response.data]

        logger.info(
            "embeddings_generated",
            count=len(embeddings),
            model=EMBEDDING_MODEL,
            tokens=response.usage.total_tokens if response.usage else 0,
        )

        return embeddings

    except Exception:
        logger.exception("embedding_failed", model=EMBEDDING_MODEL, text_count=len(texts))
        raise


async def embed_single(text: str) -> list[float]:
    """Generate embedding for a single text."""
    results = await embed_texts([text])
    return results[0]
