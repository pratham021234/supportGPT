import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.knowledge import Document, DocumentStatus
from app.repositories.vector_repo import embedding_job_repo, EmbeddingJobInternalCreate
from app.models.vector import EmbeddingJobStatus
from app.services.vector.provider import embedding_provider
from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)

class BatchEmbeddingService:
    @classmethod
    async def queue_workspace_reindex(cls, db: AsyncSession, workspace_id: str, background_tasks: BackgroundTasks):
        """
        Queues all PROCESSED or ACTIVE documents in a workspace for re-embedding.
        """
        query = select(Document).where(
            Document.workspace_id == workspace_id,
            Document.status.in_([DocumentStatus.PROCESSED])
        )
        result = await db.execute(query)
        documents = list(result.scalars().all())
        
        queued_jobs = []
        for doc in documents:
            job_in = EmbeddingJobInternalCreate(
                workspace_id=workspace_id,
                document_id=str(doc.id),
                provider=embedding_provider.name,
                status=EmbeddingJobStatus.PENDING
            )
            job = await embedding_job_repo.create(db, obj_in=job_in)
            queued_jobs.append(job)
            
            # Queue to background
            from app.services.vector.embedding_service import embedding_service
            background_tasks.add_task(
                embedding_service.process_document_embeddings,
                str(job.id),
                workspace_id,
                str(doc.id)
            )
            
        logger.info(f"Queued {len(queued_jobs)} documents for re-embedding in workspace {workspace_id}")
        return len(queued_jobs)

batch_embedding_service = BatchEmbeddingService()
