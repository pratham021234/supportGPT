from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, BackgroundTasks
import os

from app.models.knowledge import Document, DocumentStatus, SourceType
from app.repositories.knowledge_repo import document_repo, DocumentInternalCreate, knowledge_source_repo
from app.services.storage_service import storage_service
from app.core.exceptions import BadRequestException
from app.services.processing.validation import file_validation_service
from app.services.processing.duplicate import duplicate_document_service
from app.services.processing.versioning import document_versioning_service
from app.services.processing.metadata import metadata_service
from app.repositories.processing_repo import processing_job_repo, ProcessingJobInternalCreate
from app.models.processing import JobStatus

class DocumentIngestionService:
    async def upload_document(
        self, db: AsyncSession, workspace_id: str, user_id: str, 
        file: UploadFile, source_id: Optional[str] = None
    ) -> Document:
        
        # 1. Validate File
        _, val_meta = await file_validation_service.validate(file)
        
        # 2. Check Duplicates
        file_hash = await duplicate_document_service.compute_hash(file)
        is_duplicate = await duplicate_document_service.check_duplicate(db, workspace_id, file_hash)
        if is_duplicate:
            raise BadRequestException("A duplicate document with the same content already exists.")
            
        # 3. Handle Versioning
        version = await document_versioning_service.get_next_version(db, workspace_id, file.filename)
        
        # Determine source_type
        source_type = "TXT"
        if source_id:
            source = await knowledge_source_repo.get(db, id=source_id)
            if source:
                source_type = str(source.source_type.value)
        else:
            ext = os.path.splitext(file.filename)[1].upper().replace(".", "") if file.filename else ""
            if ext in ["PDF", "DOCX", "HTML", "TXT", "MD"]:
                if ext == "MD": ext = "MARKDOWN"
                source_type = ext
                
        # 4. Generate Metadata
        metadata = metadata_service.generate_document_metadata(
            file_name=file.filename,
            source_type=source_type,
            workspace_id=workspace_id,
            extra_meta={"file_hash": file_hash, "version": version}
        )
        
        # 5. Create Document Record
        internal_in = DocumentInternalCreate(
            workspace_id=workspace_id,
            source_id=source_id,
            title=file.filename or "Untitled",
            file_name=file.filename,
            file_type=file.content_type,
            file_size=val_meta["size"],
            created_by=user_id,
            metadata_=metadata,
            status=DocumentStatus.QUEUED
        )
        document = await document_repo.create(db, obj_in=internal_in)
        
        # 6. Store File
        try:
            storage_path = await storage_service.save_file(file, workspace_id, str(document.id))
            await document_repo.update(db, db_obj=document, obj_in={"storage_path": storage_path})
            
            # 7. Dispatch Job
            from app.tasks.knowledge_tasks import process_document_task
            job_in = ProcessingJobInternalCreate(
                workspace_id=str(document.workspace_id),
                document_id=str(document.id),
                status=JobStatus.QUEUED
            )
            job = await processing_job_repo.create(db, obj_in=job_in)
            
            process_document_task.delay(
                str(job.id), storage_path, source_type, str(document.workspace_id), str(document.id)
            )
            
            await document_repo.update(db, db_obj=document, obj_in={"status": DocumentStatus.PROCESSING})
            
        except Exception as e:
            await document_repo.update(db, db_obj=document, obj_in={"status": DocumentStatus.FAILED})
            raise BadRequestException(f"Ingestion failed: {str(e)}")

        return document

document_ingestion_service = DocumentIngestionService()
