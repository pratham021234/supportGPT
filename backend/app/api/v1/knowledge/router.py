from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.vector.search_service import search_service

from .sources import router as sources_router
from .documents import router as documents_router
from .faqs import router as faqs_router

knowledge_router = APIRouter()

knowledge_router.include_router(sources_router, prefix="/sources", tags=["Knowledge Sources"])
knowledge_router.include_router(documents_router, prefix="/documents", tags=["Knowledge Documents"])
knowledge_router.include_router(faqs_router, prefix="/faqs", tags=["Knowledge FAQs"])

@knowledge_router.get("/search", tags=["Knowledge Search"])
async def search_knowledge(
    query: str,
    limit: int = 10,
    document_id: str = None,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    results = await search_service.semantic_search(
        db=db,
        workspace_id=str(member.workspace_id),
        user_id=str(member.user_id),
        query=query,
        limit=limit,
        document_id=document_id
    )
    return {"results": results}

@knowledge_router.get("/health", tags=["Knowledge Health"])
async def knowledge_health(
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    from app.services.vector.qdrant_service import qdrant_service
    from sqlalchemy.future import select
    from sqlalchemy import func
    from app.models.knowledge import Document, DocumentChunk
    from app.models.processing import ProcessingJob
    
    # Get Qdrant stats
    qdrant_stats = qdrant_service.get_collection_stats(str(member.workspace_id))
    
    # Get Document counts
    doc_query = select(func.count(Document.id)).where(Document.workspace_id == str(member.workspace_id))
    doc_count = await db.scalar(doc_query)
    
    chunk_query = select(func.count(DocumentChunk.id)).where(DocumentChunk.workspace_id == str(member.workspace_id))
    chunk_count = await db.scalar(chunk_query)
    
    return {
        "status": "healthy",
        "documents_count": doc_count,
        "chunks_count": chunk_count,
        "vector_storage": qdrant_stats
    }
