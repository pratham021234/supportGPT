import asyncio
import logging
from app.core.celery_app import celery_app
from app.services.processing.pipeline import document_processing_service
from app.services.vector.embedding_service import embedding_service

logger = logging.getLogger(__name__)

# Helper to run async code inside celery synchronous workers
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(name="tasks.process_document", bind=True, max_retries=3)
def process_document_task(self, job_id: str, file_path: str, source_type: str, workspace_id: str, document_id: str):
    """
    Celery task to handle document extraction, cleaning, and chunking.
    """
    logger.info(f"Starting document processing for job {job_id}")
    try:
        # Run the extraction and chunking pipeline
        run_async(
            document_processing_service.run_pipeline(
                job_id=job_id,
                file_path=file_path,
                source_type=source_type,
                workspace_id=workspace_id,
                document_id=document_id
            )
        )
        # After extraction and chunking, queue embedding task
        from app.models.vector import EmbeddingJobStatus
        from app.repositories.vector_repo import embedding_job_repo, EmbeddingJobInternalCreate
        from app.core.database import async_session_maker
        from app.services.vector.provider import embedding_provider
        
        async def create_embedding_job():
            async with async_session_maker() as db:
                job_in = EmbeddingJobInternalCreate(
                    workspace_id=workspace_id,
                    document_id=document_id,
                    provider=embedding_provider.name,
                    status=EmbeddingJobStatus.PENDING
                )
                embedding_job = await embedding_job_repo.create(db, obj_in=job_in)
                return str(embedding_job.id)
                
        emb_job_id = run_async(create_embedding_job())
        
        # Enqueue embedding generation
        generate_embeddings_task.delay(emb_job_id, workspace_id, document_id)
        
    except Exception as exc:
        logger.error(f"Failed processing document job {job_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="tasks.generate_embeddings", bind=True, max_retries=3)
def generate_embeddings_task(self, job_id: str, workspace_id: str, document_id: str):
    """
    Celery task to generate embeddings for a processed document's chunks and index in Qdrant.
    """
    logger.info(f"Starting embeddings generation for job {job_id}")
    try:
        run_async(
            embedding_service.process_document_embeddings(
                job_id=job_id,
                workspace_id=workspace_id,
                document_id=document_id
            )
        )
    except Exception as exc:
        logger.error(f"Failed embedding generation job {job_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="tasks.process_website", bind=True, max_retries=3)
def process_website_task(self, job_id: str, url: str, workspace_id: str, document_id: str):
    """
    Celery task to handle website crawling, extraction, cleaning, and chunking.
    """
    logger.info(f"Starting website processing for job {job_id}")
    try:
        from app.services.processing.pipeline import document_processing_service
        run_async(
            document_processing_service.run_website_pipeline(
                job_id=job_id,
                url=url,
                workspace_id=workspace_id,
                document_id=document_id
            )
        )
        
        from app.models.vector import EmbeddingJobStatus
        from app.repositories.vector_repo import embedding_job_repo, EmbeddingJobInternalCreate
        from app.core.database import async_session_maker
        from app.services.vector.provider import embedding_provider
        
        async def create_embedding_job():
            async with async_session_maker() as db:
                job_in = EmbeddingJobInternalCreate(
                    workspace_id=workspace_id,
                    document_id=document_id,
                    provider=embedding_provider.name,
                    status=EmbeddingJobStatus.PENDING
                )
                embedding_job = await embedding_job_repo.create(db, obj_in=job_in)
                return str(embedding_job.id)
                
        emb_job_id = run_async(create_embedding_job())
        
        generate_embeddings_task.delay(emb_job_id, workspace_id, document_id)
        
    except Exception as exc:
        logger.error(f"Failed processing website job {job_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
