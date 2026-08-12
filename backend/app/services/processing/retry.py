from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
import logging

from app.models.processing import JobStatus
from app.repositories.processing_repo import processing_job_repo
from app.repositories.knowledge_repo import document_repo
from app.core.exceptions import BadRequestException

logger = logging.getLogger(__name__)

class RetryProcessingService:
    @classmethod
    async def retry_document_job(cls, db: AsyncSession, document_id: str, workspace_id: str):
        """
        Retries a failed document processing job.
        """
        doc = await document_repo.get(db, id=document_id)
        if not doc or str(doc.workspace_id) != workspace_id:
            raise BadRequestException("Document not found in workspace.")
            
        jobs = await processing_job_repo.get_by_document(db, document_id)
        failed_jobs = [j for j in jobs if j.status == JobStatus.FAILED]
        
        if not failed_jobs:
            raise BadRequestException("No failed processing jobs found for this document.")
            
        job = failed_jobs[-1]
        
        # Reset Job Status
        await processing_job_repo.update(db, db_obj=job, obj_in={
            "status": JobStatus.QUEUED,
            "error_message": None,
            "progress": 0
        })
        
        # Route to tasks
        from app.tasks.knowledge_tasks import process_document_task, process_website_task
        
        source_type = doc.metadata_.get("source_type", "TXT") if doc.metadata_ else "TXT"
        
        if doc.file_type == "website":
            process_website_task.delay(
                str(job.id),
                doc.file_name,
                str(doc.workspace_id),
                str(doc.id)
            )
        else:
            if doc.storage_path:
                process_document_task.delay(
                    str(job.id),
                    doc.storage_path,
                    source_type,
                    str(doc.workspace_id),
                    str(doc.id)
                )
            else:
                raise BadRequestException("Cannot retry document without storage path.")
                
        return {"status": "retry_queued", "job_id": str(job.id)}

retry_processing_service = RetryProcessingService()
