from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.rag.rag_service import rag_service

router = APIRouter()

class RAGQuery(BaseModel):
    query: str

@router.post("/query")
async def query_rag(
    query_req: RAGQuery,
    member: WorkspaceMember = Depends(require_permission("query_knowledge")),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a standard, blocking RAG query.
    """
    try:
        result = await rag_service.execute_query(
            db=db,
            workspace_id=str(member.workspace_id),
            user_id=str(member.user_id),
            query=query_req.query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/stream")
async def stream_rag(
    query_req: RAGQuery,
    member: WorkspaceMember = Depends(require_permission("query_knowledge")),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a RAG query and streams the execution events (SSE).
    """
    return StreamingResponse(
        rag_service.stream_query(
            db=db,
            workspace_id=str(member.workspace_id),
            user_id=str(member.user_id),
            query=query_req.query
        ),
        media_type="text/event-stream"
    )

@router.get("/analytics")
async def get_rag_analytics(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns basic analytics for RAG queries in the workspace.
    """
    # Quick stub for analytics
    from sqlalchemy.future import select
    from sqlalchemy import func
    from app.models.rag import QueryLog, AnswerLog, EscalationEvent
    
    # 1. Total Queries
    q1 = select(func.count(QueryLog.id)).where(QueryLog.workspace_id == member.workspace_id)
    total_queries = await db.scalar(q1)
    
    # 2. Avg Confidence
    q2 = select(func.avg(AnswerLog.confidence_score)).where(AnswerLog.workspace_id == member.workspace_id)
    avg_confidence = await db.scalar(q2) or 0.0
    
    # 3. Escalations
    q3 = select(func.count(EscalationEvent.id)).where(EscalationEvent.workspace_id == member.workspace_id)
    total_escalations = await db.scalar(q3)
    
    return {
        "total_queries": total_queries,
        "avg_confidence": round(avg_confidence, 2),
        "total_escalations": total_escalations
    }
