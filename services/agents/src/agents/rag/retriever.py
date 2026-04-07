"""RAG retriever — performs vector similarity search against firm-scoped knowledge base."""

from typing import Any

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.logging import get_logger

from agents.rag.embedder import embed_single

logger = get_logger(__name__)


async def retrieve_knowledge(
    query: str,
    firm_id: str,
    session: AsyncSession,
    top_k: int = 5,
    similarity_threshold: float = 0.7,
    knowledge_scope: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve relevant knowledge chunks using vector similarity search.

    Searches the kb_chunks table filtered by firm_id (RLS) and optional scope.
    Uses pgvector's cosine distance operator (<=>).
    """
    # Generate query embedding
    query_embedding = await embed_single(query)

    # Build the SQL query with pgvector cosine similarity
    # 1 - cosine_distance = cosine_similarity
    query_sql = """
        SELECT
            kc.id,
            kc.content,
            kc.chunk_index,
            kc.metadata,
            kd.title AS document_title,
            kd.doc_type,
            1 - (kc.embedding <=> :embedding::vector) AS similarity
        FROM kb_chunks kc
        LEFT JOIN kb_documents kd ON kc.document_id = kd.id
        WHERE kc.firm_id = :firm_id
          AND 1 - (kc.embedding <=> :embedding::vector) >= :threshold
    """

    params: dict[str, Any] = {
        "firm_id": firm_id,
        "embedding": str(query_embedding),
        "threshold": similarity_threshold,
        "top_k": top_k,
    }

    # Optional scope filter — matches against document doc_type or metadata tags
    if knowledge_scope:
        query_sql += " AND (kd.doc_type = ANY(:scope) OR kc.metadata->>'scope' = ANY(:scope))"
        params["scope"] = knowledge_scope

    query_sql += """
        ORDER BY kc.embedding <=> :embedding::vector
        LIMIT :top_k
    """

    try:
        result = await session.execute(sql_text(query_sql), params)
        rows = result.mappings().all()

        chunks = [
            {
                "id": str(row["id"]),
                "content": row["content"],
                "source": row.get("document_title", "Unknown"),
                "doc_type": row.get("doc_type"),
                "similarity": round(float(row["similarity"]), 4),
                "chunk_index": row.get("chunk_index", 0),
            }
            for row in rows
        ]

        logger.info(
            "knowledge_retrieved",
            firm_id=firm_id,
            query_preview=query[:80],
            results=len(chunks),
            top_similarity=chunks[0]["similarity"] if chunks else 0,
        )

        return chunks

    except Exception:
        logger.exception("knowledge_retrieval_failed", firm_id=firm_id)
        return []


async def retrieve_faq(
    query: str,
    firm_id: str,
    session: AsyncSession,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    Search FAQ entries using vector similarity on the question embedding.

    FAQs are stored as structured Q&A pairs with pre-computed embeddings.
    """
    query_embedding = await embed_single(query)

    faq_sql = """
        SELECT
            id,
            question,
            answer,
            category,
            1 - (question_embedding <=> :embedding::vector) AS similarity
        FROM kb_faqs
        WHERE firm_id = :firm_id
          AND is_active = true
          AND 1 - (question_embedding <=> :embedding::vector) >= 0.75
        ORDER BY question_embedding <=> :embedding::vector
        LIMIT :top_k
    """

    try:
        result = await session.execute(sql_text(faq_sql), {
            "firm_id": firm_id,
            "embedding": str(query_embedding),
            "top_k": top_k,
        })
        rows = result.mappings().all()

        faqs = [
            {
                "question": row["question"],
                "answer": row["answer"],
                "category": row.get("category"),
                "similarity": round(float(row["similarity"]), 4),
                "source": "FAQ",
            }
            for row in rows
        ]

        logger.info("faq_retrieved", firm_id=firm_id, results=len(faqs))
        return faqs

    except Exception:
        logger.exception("faq_retrieval_failed", firm_id=firm_id)
        return []
