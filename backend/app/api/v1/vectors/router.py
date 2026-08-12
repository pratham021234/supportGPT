from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.models.vector import EmbeddingJobStatus
from app.repositories.vector_repo import embedding_job_repo, EmbeddingJobInternalCreate
from app.services.vector.search_service import search_service
from app.services.vector.qdrant_service import qdrant_service
from app.services.vector.embedding_service import embedding_service
from app.services.vector.provider import embedding_provider
from app.services.vector.health_service import vector_health_service
from app.services.vector.reindex_service import reindex_service
from app.services.vector.batch_service import batch_embedding_service

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    document_id: Optional[str] = None
    agent_id: Optional[str] = None

@router.post("/search/semantic")
async def semantic_search(
    query: SearchQuery,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    """Executes a semantic search against the workspace collection."""
    results = await search_service.semantic_search(
        db=db,
        workspace_id=str(member.workspace_id),
        user_id=str(member.user_id),
        query=query.query,
        limit=query.limit,
        document_id=query.document_id,
        agent_id=query.agent_id
    )
    return {"results": results}

@router.get("/collections/stats")
async def collection_stats(
    member: WorkspaceMember = Depends(require_permission("knowledge:read"))
):
    """Returns Qdrant collection stats for the workspace."""
    stats = qdrant_service.get_collection_stats(str(member.workspace_id))
    return stats

@router.post("/embeddings/jobs")
async def create_embedding_job(
    document_id: str,
    background_tasks: BackgroundTasks,
    member: WorkspaceMember = Depends(require_permission("knowledge:write")),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually triggers embedding generation for a document's chunks.
    Typically, this is triggered automatically by the processing pipeline.
    """
    job_in = EmbeddingJobInternalCreate(
        workspace_id=str(member.workspace_id),
        document_id=document_id,
        provider=embedding_provider.name,
        status=EmbeddingJobStatus.PENDING
    )
    job = await embedding_job_repo.create(db, obj_in=job_in)
    
    background_tasks.add_task(
        embedding_service.process_document_embeddings,
        str(job.id),
        str(member.workspace_id),
        document_id
    )
    
    return {"job_id": job.id, "status": "QUEUED"}

@router.get("/health")
async def get_vector_health(
    member: WorkspaceMember = Depends(require_permission("knowledge:read"))
):
    """Returns cluster health for vector services."""
    return vector_health_service.get_cluster_health()

@router.post("/reindex")
async def queue_reindex(
    background_tasks: BackgroundTasks,
    member: WorkspaceMember = Depends(require_permission("knowledge:write")),
    db: AsyncSession = Depends(get_db)
):
    """Queues a reindex of all existing documents without dropping the collection."""
    count = await batch_embedding_service.queue_workspace_reindex(db, str(member.workspace_id), background_tasks)
    return {"status": "QUEUED", "jobs_created": count}

@router.post("/rebuild")
async def rebuild_collection(
    background_tasks: BackgroundTasks,
    member: WorkspaceMember = Depends(require_permission("knowledge:write")),
    db: AsyncSession = Depends(get_db)
):
    """Drops the entire workspace collection and re-embeds everything."""
    count = await reindex_service.rebuild_workspace_collection(db, str(member.workspace_id), background_tasks)
    return {"status": "REBUILD_QUEUED", "jobs_created": count}
