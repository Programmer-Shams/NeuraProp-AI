"""Document ingestor — processes uploaded documents into embeddable chunks and stores them."""

import uuid
from typing import Any

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.logging import get_logger

from agents.rag.chunker import chunk_text
from agents.rag.embedder import embed_texts

logger = get_logger(__name__)

# Batch size for embedding API calls
EMBED_BATCH_SIZE = 100


async def ingest_document(
    firm_id: str,
    document_id: str,
    title: str,
    content: str,
    doc_type: str,
    session: AsyncSession,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> dict[str, Any]:
    """
    Ingest a document into the knowledge base.

    Pipeline: text → chunk → embed → store in kb_chunks with pgvector.
    """
    logger.info(
        "ingesting_document",
        firm_id=firm_id,
        document_id=document_id,
        title=title,
        content_length=len(content),
    )

    # Chunk the document
    chunks = chunk_text(
        text=content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        document_id=document_id,
        source=title,
    )

    if not chunks:
        logger.warning("no_chunks_generated", document_id=document_id)
        return {"chunks_created": 0}

    # Delete existing chunks for this document (re-ingestion)
    await session.execute(
        sql_text("DELETE FROM kb_chunks WHERE document_id = :doc_id AND firm_id = :firm_id"),
        {"doc_id": document_id, "firm_id": firm_id},
    )

    # Embed in batches
    total_stored = 0
    for i in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[i : i + EMBED_BATCH_SIZE]
        texts = [c.content for c in batch]
        embeddings = await embed_texts(texts)

        # Store chunks with embeddings
        for chunk, embedding in zip(batch, embeddings):
            chunk_id = str(uuid.uuid4())
            await session.execute(
                sql_text("""
                    INSERT INTO kb_chunks (id, firm_id, document_id, content, embedding, chunk_index, metadata)
                    VALUES (:id, :firm_id, :doc_id, :content, :embedding::vector, :chunk_index, :metadata::jsonb)
                """),
                {
                    "id": chunk_id,
                    "firm_id": firm_id,
                    "doc_id": document_id,
                    "content": chunk.content,
                    "embedding": str(embedding),
                    "chunk_index": chunk.chunk_index,
                    "metadata": "{}",
                },
            )
            total_stored += 1

    await session.commit()

    logger.info(
        "document_ingested",
        document_id=document_id,
        chunks_created=total_stored,
    )

    return {"chunks_created": total_stored, "document_id": document_id}


async def ingest_faq(
    firm_id: str,
    question: str,
    answer: str,
    category: str | None,
    session: AsyncSession,
) -> dict[str, Any]:
    """
    Ingest a single FAQ entry — embed the question for similarity search.
    """
    embedding = (await embed_texts([question]))[0]
    faq_id = str(uuid.uuid4())

    await session.execute(
        sql_text("""
            INSERT INTO kb_faqs (id, firm_id, question, answer, category, question_embedding, is_active)
            VALUES (:id, :firm_id, :question, :answer, :category, :embedding::vector, true)
        """),
        {
            "id": faq_id,
            "firm_id": firm_id,
            "question": question,
            "answer": answer,
            "category": category,
            "embedding": str(embedding),
        },
    )
    await session.commit()

    logger.info("faq_ingested", firm_id=firm_id, faq_id=faq_id)
    return {"faq_id": faq_id}
