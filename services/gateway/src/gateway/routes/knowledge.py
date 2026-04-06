"""Knowledge base management endpoints."""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import func, select

from neuraprop_core.logging import get_logger
from neuraprop_core.models.knowledge import KBDocument, KBFaq
from neuraprop_core.s3 import upload_file

from gateway.deps import DB, FirmId

logger = get_logger(__name__)
router = APIRouter()


class CreateFaqRequest(BaseModel):
    question: str
    answer: str
    category: str | None = None
    tags: list[str] = []


@router.get("/knowledge/documents")
async def list_documents(
    firm_id: FirmId,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """List knowledge base documents."""
    query = select(KBDocument).where(KBDocument.firm_id == firm_id)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(KBDocument.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "items": [
            {
                "id": str(d.id),
                "title": d.title,
                "source_type": d.source_type,
                "status": d.status,
                "chunk_count": d.chunk_count,
                "tags": d.tags,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/knowledge/documents/upload")
async def upload_document(
    firm_id: FirmId,
    db: DB,
    file: UploadFile = File(...),
    title: str | None = None,
) -> dict:
    """Upload a document to the knowledge base."""
    content = await file.read()
    s3_key = f"{firm_id}/documents/{file.filename}"

    await upload_file(
        key=s3_key,
        data=content,
        content_type=file.content_type or "application/octet-stream",
    )

    doc = KBDocument(
        firm_id=firm_id,
        title=title or file.filename or "Untitled",
        source_type="upload",
        s3_key=s3_key,
        content_type=file.content_type,
        file_size=len(content),
        status="processing",
    )
    db.add(doc)
    await db.flush()

    logger.info("document_uploaded", firm_id=firm_id, doc_id=str(doc.id), title=doc.title)

    return {
        "id": str(doc.id),
        "title": doc.title,
        "status": "processing",
        "message": "Document uploaded. Processing will begin shortly.",
    }


@router.get("/knowledge/faqs")
async def list_faqs(firm_id: FirmId, db: DB) -> dict:
    """List FAQ entries."""
    query = select(KBFaq).where(KBFaq.firm_id == firm_id).order_by(KBFaq.created_at.desc())
    result = await db.execute(query)
    faqs = result.scalars().all()

    return {
        "items": [
            {
                "id": str(f.id),
                "question": f.question,
                "answer": f.answer,
                "category": f.category,
                "tags": f.tags,
                "enabled": f.enabled,
            }
            for f in faqs
        ]
    }


@router.post("/knowledge/faqs")
async def create_faq(body: CreateFaqRequest, firm_id: FirmId, db: DB) -> dict:
    """Create a new FAQ entry."""
    faq = KBFaq(
        firm_id=firm_id,
        question=body.question,
        answer=body.answer,
        category=body.category,
        tags=body.tags,
    )
    db.add(faq)
    await db.flush()

    return {
        "id": str(faq.id),
        "question": faq.question,
        "answer": faq.answer,
        "category": faq.category,
    }
