from typing import List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from uuid import UUID

from app.models.knowledge import KnowledgeSource, Document, FAQ, DocumentStatus, SourceType
from app.repositories.knowledge_repo import (
    knowledge_source_repo, document_repo, faq_repo, knowledge_tag_repo,
    KnowledgeSourceInternalCreate, DocumentInternalCreate, FAQInternalCreate
)
from app.schemas.knowledge import (
    KnowledgeSourceCreate, KnowledgeSourceUpdate,
    DocumentUpdate, FAQCreate, FAQUpdate
)
from app.services.storage_service import storage_service
from app.core.exceptions import NotFoundException, BadRequestException
from fastapi import BackgroundTasks
import asyncio

class KnowledgeService:
    # --- Sources ---
    async def create_source(self, db: AsyncSession, workspace_id: str, user_id: str, obj_in: KnowledgeSourceCreate) -> KnowledgeSource:
        internal_in = KnowledgeSourceInternalCreate(
            workspace_id=workspace_id,
            name=obj_in.name,
            description=obj_in.description,
            source_type=obj_in.source_type,
            created_by=user_id
        )
        return await knowledge_source_repo.create(db, obj_in=internal_in)

    async def get_workspace_sources_paginated(
        self, db: AsyncSession, workspace_id: str, pagination: Any, filters: Any
    ) -> dict:
        return await knowledge_source_repo.get_paginated(
            db, pagination=pagination, filters=filters, workspace_id=workspace_id
        )

    async def get_workspace_sources(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[KnowledgeSource]:
        return await knowledge_source_repo.get_by_workspace(db, workspace_id, skip, limit)

    async def update_source(self, db: AsyncSession, source_id: str, workspace_id: str, obj_in: KnowledgeSourceUpdate) -> KnowledgeSource:
        source = await knowledge_source_repo.get(db, id=source_id)
        if not source or str(source.workspace_id) != workspace_id:
            raise NotFoundException("Knowledge source not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        return await knowledge_source_repo.update(db, db_obj=source, obj_in=update_data)

    async def delete_source(self, db: AsyncSession, source_id: str, workspace_id: str) -> bool:
        source = await knowledge_source_repo.get(db, id=source_id)
        if not source or str(source.workspace_id) != workspace_id:
            raise NotFoundException("Knowledge source not found")
        
        # When deleting a source, we might need to delete associated documents locally
        # Cascade handles the DB, but not the physical files. 
        # A background worker usually handles cleanup. Here we just rely on cascade.
        await knowledge_source_repo.remove(db, id=source_id)
        return True

    # --- Documents ---
    async def upload_document(
        self, db: AsyncSession, workspace_id: str, user_id: str, 
        file: UploadFile, source_id: Optional[str] = None,
        background_tasks: BackgroundTasks = None
    ) -> Document:
        # Create initial document record
        internal_in = DocumentInternalCreate(
            workspace_id=workspace_id,
            source_id=source_id,
            title=file.filename or "Untitled",
            file_name=file.filename,
            file_type=file.content_type,
            file_size=file.size if hasattr(file, 'size') else 0, # Depending on FastAPI version, size might need computation
            created_by=user_id
        )
        document = await document_repo.create(db, obj_in=internal_in)
        
        # Save file physically
        try:
            storage_path = await storage_service.save_file(file, workspace_id, str(document.id))
            
            # Update document with storage path
            await document_repo.update(db, db_obj=document, obj_in={"storage_path": storage_path})
            
            # Stub: Emulate sending to processing queue
            await self._queue_document_processing(db, document, background_tasks)
            
        except Exception as e:
            await document_repo.update(db, db_obj=document, obj_in={"status": DocumentStatus.FAILED})
            raise BadRequestException(f"File processing failed: {str(e)}")

        return document

    async def _queue_document_processing(self, db: AsyncSession, document: Document, background_tasks: BackgroundTasks = None):
        """
        Creates a ProcessingJob and enqueues the process_document_task via Celery.
        """
        from app.models.processing import JobStatus
        from app.repositories.processing_repo import processing_job_repo, ProcessingJobInternalCreate
        from app.tasks.knowledge_tasks import process_document_task
        
        # Create Job
        job_in = ProcessingJobInternalCreate(
            workspace_id=str(document.workspace_id),
            document_id=str(document.id),
            status=JobStatus.QUEUED
        )
        job = await processing_job_repo.create(db, obj_in=job_in)
        
        # We need the source_type for extraction
        source_type = "TXT" # default fallback
        if document.source_id:
            from app.repositories.knowledge_repo import knowledge_source_repo
            source = await knowledge_source_repo.get(db, id=str(document.source_id))
            if source:
                source_type = str(source.source_type.value)
        else:
            # Guess from file extension if no source container
            import os
            ext = os.path.splitext(document.file_name)[1].upper().replace(".", "") if document.file_name else ""
            if ext in ["PDF", "DOCX", "HTML", "TXT", "MD"]:
                if ext == "MD": ext = "MARKDOWN"
                source_type = ext
        
        # Enqueue Task via Celery
        if document.storage_path:
            process_document_task.delay(
                str(job.id),
                document.storage_path,
                source_type,
                str(document.workspace_id),
                str(document.id)
            )
        
        await document_repo.update(db, db_obj=document, obj_in={"status": DocumentStatus.PROCESSING})

    async def process_website(
        self, db: AsyncSession, workspace_id: str, user_id: str, 
        url: str, source_id: Optional[str] = None
    ) -> Document:
        # Create initial document record for website
        internal_in = DocumentInternalCreate(
            workspace_id=workspace_id,
            source_id=source_id,
            title=url,
            file_name=url,
            file_type="website",
            file_size=0,
            created_by=user_id
        )
        document = await document_repo.create(db, obj_in=internal_in)
        
        from app.models.processing import JobStatus
        from app.repositories.processing_repo import processing_job_repo, ProcessingJobInternalCreate
        from app.tasks.knowledge_tasks import process_website_task
        
        job_in = ProcessingJobInternalCreate(
            workspace_id=str(document.workspace_id),
            document_id=str(document.id),
            status=JobStatus.QUEUED
        )
        job = await processing_job_repo.create(db, obj_in=job_in)
        
        process_website_task.delay(
            str(job.id),
            url,
            str(document.workspace_id),
            str(document.id)
        )
        
        await document_repo.update(db, db_obj=document, obj_in={"status": DocumentStatus.PROCESSING})
        return document

    async def get_workspace_documents_paginated(
        self, db: AsyncSession, workspace_id: str, pagination: Any, filters: Any
    ) -> dict:
        return await document_repo.get_paginated(
            db, pagination=pagination, filters=filters, workspace_id=workspace_id
        )

    async def get_workspace_documents(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        return await document_repo.get_by_workspace(db, workspace_id, skip, limit)
    
    async def get_document(self, db: AsyncSession, document_id: str, workspace_id: str) -> Document:
        document = await document_repo.get_with_tags(db, id=document_id)
        if not document or str(document.workspace_id) != workspace_id:
            raise NotFoundException("Document not found")
        return document

    async def delete_document(self, db: AsyncSession, document_id: str, workspace_id: str) -> bool:
        document = await document_repo.get(db, id=document_id)
        if not document or str(document.workspace_id) != workspace_id:
            raise NotFoundException("Document not found")
        
        if document.storage_path:
            await storage_service.delete_file(document.storage_path)
            
        await document_repo.remove(db, id=document_id)
        return True

    async def update_document(self, db: AsyncSession, document_id: str, workspace_id: str, obj_in: DocumentUpdate) -> Document:
        document = await document_repo.get(db, id=document_id)
        if not document or str(document.workspace_id) != workspace_id:
            raise NotFoundException("Document not found")
        update_data = obj_in.model_dump(exclude_unset=True)
        return await document_repo.update(db, db_obj=document, obj_in=update_data)

    async def reprocess_document(self, db: AsyncSession, document_id: str, workspace_id: str, user_id: str) -> bool:
        doc = await self.get_document(db, document_id, workspace_id)
        if doc.file_type == "website":
            await self.process_website(db, workspace_id, user_id, doc.file_name, str(doc.source_id) if doc.source_id else None)
        else:
            if doc.storage_path:
                await self._queue_document_processing(db, doc)
        return True

    # --- FAQs ---
    async def create_faq(self, db: AsyncSession, workspace_id: str, user_id: str, obj_in: FAQCreate) -> FAQ:
        internal_in = FAQInternalCreate(
            workspace_id=workspace_id,
            question=obj_in.question,
            answer=obj_in.answer,
            category=obj_in.category,
            created_by=user_id
        )
        return await faq_repo.create(db, obj_in=internal_in)

    async def get_workspace_faqs_paginated(
        self, db: AsyncSession, workspace_id: str, pagination: Any, filters: Any
    ) -> dict:
        return await faq_repo.get_paginated(
            db, pagination=pagination, filters=filters, workspace_id=workspace_id
        )

    async def get_workspace_faqs(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[FAQ]:
        return await faq_repo.get_by_workspace(db, workspace_id, skip, limit)

    async def update_faq(self, db: AsyncSession, faq_id: str, workspace_id: str, obj_in: FAQUpdate) -> FAQ:
        faq = await faq_repo.get(db, id=faq_id)
        if not faq or str(faq.workspace_id) != workspace_id:
            raise NotFoundException("FAQ not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        return await faq_repo.update(db, db_obj=faq, obj_in=update_data)

    async def delete_faq(self, db: AsyncSession, faq_id: str, workspace_id: str) -> bool:
        faq = await faq_repo.get(db, id=faq_id)
        if not faq or str(faq.workspace_id) != workspace_id:
            raise NotFoundException("FAQ not found")
            
        await faq_repo.remove(db, id=faq_id)
        return True

knowledge_service = KnowledgeService()
