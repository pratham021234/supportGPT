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

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    source_id: Optional[str] = Form(None),
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    return await document_ingestion_service.upload_document(
        db, str(member.workspace_id), str(member.user_id), file, source_id
    )

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
