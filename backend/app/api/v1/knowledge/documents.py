from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.schemas.knowledge import DocumentResponse
from app.services.knowledge_service import knowledge_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    source_id: Optional[str] = Form(None),
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.upload_document(
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

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.get_workspace_documents(db, str(member.workspace_id), skip, limit)

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

@router.post("/{document_id}/reprocess", status_code=status.HTTP_202_ACCEPTED)
async def reprocess_document(
    document_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve document, if it's website queue website task, if file queue document task.
    # We will assume a minimal implementation here that queues document process
    doc = await knowledge_service.get_document(db, document_id, str(member.workspace_id))
    if doc.file_type == "website":
        await knowledge_service.process_website(db, str(member.workspace_id), str(member.user_id), doc.file_name, str(doc.source_id) if doc.source_id else None)
    else:
        # Re-enqueuing relies on having the file still in storage.
        if doc.storage_path:
            from app.tasks.knowledge_tasks import process_document_task
            from app.models.processing import JobStatus
            from app.repositories.processing_repo import processing_job_repo, ProcessingJobInternalCreate
            from app.models.knowledge import DocumentStatus
            from app.repositories.knowledge_repo import document_repo
            
            job_in = ProcessingJobInternalCreate(
                workspace_id=str(doc.workspace_id),
                document_id=str(doc.id),
                status=JobStatus.QUEUED
            )
            job = await processing_job_repo.create(db, obj_in=job_in)
            process_document_task.delay(
                str(job.id),
                doc.storage_path,
                "TXT", # Simplification
                str(doc.workspace_id),
                str(doc.id)
            )
            await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.PROCESSING})
    return {"status": "reprocessing_queued"}
