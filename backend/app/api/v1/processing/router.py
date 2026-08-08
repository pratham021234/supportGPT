from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.repositories.processing_repo import processing_job_repo
from app.repositories.knowledge_repo import document_repo

# We need response schemas, but for brevity we'll just return Any / dicts
# In a real app we'd define these in app.schemas.processing
router = APIRouter()

@router.get("/jobs", response_model=List[Any])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    """List background processing jobs for the workspace."""
    jobs = await processing_job_repo.get_by_workspace(db, str(member.workspace_id), skip, limit)
    return jobs

@router.get("/documents/{document_id}/chunks", response_model=List[Any])
async def get_document_chunks(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve chunks for a given document."""
    from sqlalchemy.future import select
    from app.models.knowledge import DocumentChunk
    
    doc = await document_repo.get(db, id=document_id)
    if not doc or str(doc.workspace_id) != str(member.workspace_id):
        raise HTTPException(status_code=404, detail="Document not found")
        
    query = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
    result = await db.execute(query)
    return list(result.scalars().all())

@router.get("/analytics", response_model=Any)
async def processing_analytics(
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    """Basic processing analytics."""
    from sqlalchemy import func
    from app.models.processing import ProcessingJob
    
    query = select(ProcessingJob.status, func.count(ProcessingJob.id)).where(ProcessingJob.workspace_id == str(member.workspace_id)).group_by(ProcessingJob.status)
    result = await db.execute(query)
    
    stats = {row[0].value: row[1] for row in result.all()}
    return {"status_counts": stats}
