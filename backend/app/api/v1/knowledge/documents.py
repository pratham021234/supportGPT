from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.schemas.knowledge import DocumentResponse, DocumentUpdate
from app.schemas.common import PaginationParams, FilterParams, PaginatedResponse
from app.services.knowledge_service import knowledge_service
from app.services.knowledge_ingestion import document_ingestion_service
from app.services.processing.retry import retry_processing_service
from app.services.billing.billing_service import plan_enforcement_service, usage_tracking_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    source_id: Optional[str] = Form(None),
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    # Security Validation
    allowed_types = ["application/pdf", "text/plain", "text/markdown", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/csv"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        
    try:
        await plan_enforcement_service.check_limit(db, str(member.workspace_id), "documents", 1.0)
    except plan_enforcement_service.LimitExceededError as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    # Read the first chunk to determine size or set a soft limit based on content-length header
    # For robust validation we'd stream it and break if it exceeds MAX_SIZE.
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")

    doc = await document_ingestion_service.upload_document(
        db, str(member.workspace_id), str(member.user_id), file, source_id
    )
    await usage_tracking_service.track_usage(db, str(member.workspace_id), "documents", 1.0)
    return doc

from pydantic import BaseModel
class WebsiteUpload(BaseModel):
    url: str
    source_id: Optional[str] = None

@router.post("/website", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def crawl_website(
    payload: WebsiteUpload,
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.process_website(
        db, str(member.workspace_id), str(member.user_id), payload.url, payload.source_id
    )

@router.get("/", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.get_workspace_documents_paginated(db, str(member.workspace_id), pagination, filters)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.get_document(db, document_id, str(member.workspace_id))

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:delete")),
    db: AsyncSession = Depends(get_db)
):
    await knowledge_service.delete_document(db, document_id, str(member.workspace_id))

@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    obj_in: DocumentUpdate,
    member: WorkspaceMember = Depends(require_permission("knowledge:manage")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.update_document(db, document_id, str(member.workspace_id), obj_in)

@router.get("/{document_id}/metadata")
async def get_document_metadata(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    doc = await knowledge_service.get_document(db, document_id, str(member.workspace_id))
    return {
        "id": str(doc.id),
        "title": doc.title,
        "file_name": doc.file_name,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "status": doc.status,
        "metadata": doc.metadata_,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at
    }

@router.post("/{document_id}/reindex", status_code=status.HTTP_202_ACCEPTED)
async def reindex_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    # For now, reindex simply re-queues processing
    await retry_processing_service.retry_document_job(db, document_id, str(member.workspace_id))
    return {"status": "reindexing_queued"}

@router.post("/{document_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    await retry_processing_service.retry_document_job(db, document_id, str(member.workspace_id))
    return {"status": "retry_queued"}

@router.post("/{document_id}/reprocess", status_code=status.HTTP_202_ACCEPTED)
async def reprocess_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    await retry_processing_service.retry_document_job(db, document_id, str(member.workspace_id))
    return {"status": "reprocessing_queued"}

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    from app.repositories.processing_repo import processing_job_repo
    jobs = await processing_job_repo.get_by_document(db, document_id)
    if not jobs:
        raise HTTPException(status_code=404, detail="No processing jobs found.")
    job = jobs[-1]
    return {
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }

@router.get("/{document_id}/extraction")
async def get_document_extraction(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    from app.repositories.processing_repo import extraction_result_repo
    ext = await extraction_result_repo.get_by_document(db, document_id)
    if not ext:
        raise HTTPException(status_code=404, detail="No extraction results found.")
    return {
        "page_count": ext.page_count,
        "character_count": ext.character_count,
        "word_count": ext.word_count,
        "detected_language": ext.detected_language,
        "cleaned_text": ext.cleaned_text[:1000] if ext.cleaned_text else "",  # Return a preview
        "metadata": ext.metadata_
    }

from pydantic import BaseModel
class RechunkRequest(BaseModel):
    chunk_strategy: str
    chunk_size: int
    chunk_overlap: int

@router.post("/{document_id}/rechunk", status_code=status.HTTP_202_ACCEPTED)
async def rechunk_document(
    document_id: str,
    payload: RechunkRequest,
    member: WorkspaceMember = Depends(require_permission("knowledge:manage")),
    db: AsyncSession = Depends(get_db)
):
    from app.services.processing.retry import retry_processing_service
    # Update document with new metadata settings for chunking
    doc = await knowledge_service.get_document(db, document_id, str(member.workspace_id))
    meta = doc.metadata_ or {}
    meta["chunk_strategy"] = payload.chunk_strategy
    meta["chunk_size"] = payload.chunk_size
    meta["chunk_overlap"] = payload.chunk_overlap
    
    await knowledge_service.update_document(
        db, document_id, str(member.workspace_id), DocumentUpdate(metadata_=meta)
    )
    
    # Retry the job which will pick up the new chunking settings during pipeline execution
    await retry_processing_service.retry_document_job(db, document_id, str(member.workspace_id))
    return {"status": "rechunking_queued"}

@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    from app.repositories.knowledge_repo import document_chunk_repo
    # Verify document belongs to workspace
    await knowledge_service.get_document(db, document_id, str(member.workspace_id))
    
    chunks = await document_chunk_repo.get_by_document(db, document_id)
    
    # Return serializable summary
    result = []
    for c in chunks:
        result.append({
            "id": str(c.id),
            "chunk_index": c.chunk_index,
            "content": c.content,
            "token_count": c.token_count,
            "character_count": c.character_count,
            "section": c.section,
            "page_number": c.page_number,
            "parent_heading": c.parent_heading,
            "chunk_type": c.chunk_type,
            "metadata": c.metadata_
        })
    return {"chunks": result, "total": len(result)}

@router.post("/{document_id}/reembed", status_code=status.HTTP_202_ACCEPTED)
async def reembed_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:manage")),
    db: AsyncSession = Depends(get_db)
):
    from app.services.vector.embedding_service import embedding_service
    # Verify document belongs to workspace
    await knowledge_service.get_document(db, document_id, str(member.workspace_id))
    
    result = await embedding_service.reembed_document(str(member.workspace_id), document_id)
    return result

