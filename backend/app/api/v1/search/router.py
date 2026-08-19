from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.vector.search_service import search_service
from app.services.vector.health_service import vector_health_service
from app.services.vector.reindex_service import reindex_service

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

@router.post("/semantic", summary="Perform Semantic Search")
async def semantic_search(
    request: SearchRequest,
    member: WorkspaceMember = Depends(require_permission("search:read")),
    db: AsyncSession = Depends(get_db)
):
    results = await search_service.semantic_search(
        db=db,
        workspace_id=str(member.workspace_id),
        user_id=str(member.user_id),
        query=request.query,
        limit=request.limit,
        filters=request.filters
    )
    return {"results": results}

@router.post("/hybrid", summary="Perform Hybrid Search")
async def hybrid_search(
    request: SearchRequest,
    member: WorkspaceMember = Depends(require_permission("search:read")),
    db: AsyncSession = Depends(get_db)
):
    results = await search_service.hybrid_search(
        db=db,
        workspace_id=str(member.workspace_id),
        user_id=str(member.user_id),
        query=request.query,
        limit=request.limit,
        filters=request.filters
    )
    return {"results": results}

@router.get("/health", summary="Get Vector Health")
async def get_vector_health(
    member: WorkspaceMember = Depends(require_permission("search:read")),
    db: AsyncSession = Depends(get_db)
):
    health = vector_health_service.get_cluster_health()
    return health

@router.get("/analytics", summary="Get Search Analytics")
async def get_search_analytics(
    member: WorkspaceMember = Depends(require_permission("search:read")),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve analytics from search_event_repo
    from app.repositories.vector_repo import search_event_repo
    
    # Very simple analytics for MVP
    events = await search_event_repo.get_by_workspace(db, str(member.workspace_id))
    
    total_searches = len(events)
    semantic_count = sum(1 for e in events if e.search_type == "SEMANTIC")
    hybrid_count = sum(1 for e in events if e.search_type == "HYBRID")
    avg_latency = sum(e.latency_ms or 0 for e in events) / total_searches if total_searches else 0
    
    return {
        "total_searches": total_searches,
        "semantic_count": semantic_count,
        "hybrid_count": hybrid_count,
        "avg_latency_ms": int(avg_latency)
    }

@router.post("/reindex", summary="Reindex entire workspace collection", status_code=status.HTTP_202_ACCEPTED)
async def reindex_workspace(
    background_tasks: BackgroundTasks,
    member: WorkspaceMember = Depends(require_permission("search:manage")),
    db: AsyncSession = Depends(get_db)
):
    queued = await reindex_service.rebuild_workspace_collection(
        db=db, 
        workspace_id=str(member.workspace_id), 
        background_tasks=background_tasks
    )
    return {"message": f"Reindex started for {queued} documents", "queued": queued}
