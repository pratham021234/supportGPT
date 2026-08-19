import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from qdrant_client.http import models as rest  # type: ignore
from typing import List

from app.models.vector import EmbeddingJobStatus
from app.models.knowledge import DocumentChunk, Document
from app.repositories.vector_repo import embedding_job_repo, embedding_record_repo, EmbeddingRecord
from app.services.vector.provider import embedding_provider
from app.services.vector.qdrant_service import qdrant_service
from app.services.vector.cache_service import embedding_cache_service
from app.services.vector.validation_service import embedding_validation_service
from app.services.vector.quality_service import embedding_quality_service
from app.core.database import async_session_maker
import time
import asyncio

logger = logging.getLogger(__name__)

class EmbeddingService:
    async def process_document_embeddings(self, job_id: str, workspace_id: str, document_id: str):
        """
        Background worker process to generate embeddings for a document's chunks.
        """
        async with async_session_maker() as db:
            job = await embedding_job_repo.get(db, id=job_id)
            if not job:
                logger.error(f"Embedding job {job_id} not found.")
                return

            try:
                # 1. Ensure Collection Exists
                qdrant_service.ensure_collection(workspace_id, embedding_provider.dimension)

                # 2. Update Status
                await embedding_job_repo.update(db, db_obj=job, obj_in={
                    "status": EmbeddingJobStatus.PROCESSING,
                    "started_at": datetime.utcnow()
                })

                # 3. Fetch Document to get basic metadata
                from app.repositories.knowledge_repo import document_repo
                doc = await document_repo.get(db, id=document_id)
                document_title = doc.title if doc else "Unknown"
                
                # Check for agent_id on document (if it's tied to an agent source)
                agent_id = None
                if doc and doc.source_id:
                    # If this is linked to a source, that source might be tied to an agent
                    # For strict agent isolation, we usually store this in doc metadata
                    pass
                if doc and doc.metadata_:
                    agent_id = doc.metadata_.get("agent_id")

                # 4. Fetch Chunks
                query = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
                result = await db.execute(query)
                chunks = list(result.scalars().all())

                if not chunks:
                    logger.warning(f"No chunks found for document {document_id}")
                    await embedding_job_repo.update(db, db_obj=job, obj_in={
                        "status": EmbeddingJobStatus.COMPLETED,
                        "completed_at": datetime.utcnow()
                    })
                    return

                # 5. Process in Batches
                batch_size = 100
                total_chunks = len(chunks)
                
                for i in range(0, total_chunks, batch_size):
                    batch = chunks[i:i + batch_size]
                    
                    # Prepare for generation and caching
                    points = []
                    records_to_create = []
                    texts_to_embed = []
                    chunks_to_embed = []
                    
                    for chunk in batch:
                        chunk_hash = embedding_cache_service.compute_hash(chunk.content)
                        cached_chunk_id = await embedding_cache_service.get_cached_record(db, chunk_hash)
                        
                        if cached_chunk_id and cached_chunk_id == str(chunk.id):
                            # Already embedded and valid for this exact chunk
                            continue
                            
                        # Needs embedding
                        texts_to_embed.append(chunk.content)
                        chunks_to_embed.append((chunk, chunk_hash))

                    if texts_to_embed:
                        # Retry loop for generation
                        max_retries = 3
                        embeddings = None
                        for attempt in range(max_retries):
                            try:
                                start_time = time.time()
                                embeddings = await embedding_provider.embed_texts(texts_to_embed)
                                latency_ms = int((time.time() - start_time) * 1000)
                                embedding_quality_service.record_call(embedding_provider.name, latency_ms, success=True)
                                break
                            except Exception as e:
                                logger.warning(f"Embedding attempt {attempt+1} failed: {e}")
                                embedding_quality_service.record_call(embedding_provider.name, 0, success=False)
                                if attempt == max_retries - 1:
                                    raise e
                                await asyncio.sleep(2 ** attempt) # Exponential backoff

                        # 6. Validate and Format for Qdrant
                        for (chunk, chunk_hash), vector in zip(chunks_to_embed, embeddings):
                            if not embedding_validation_service.is_valid_vector(vector, embedding_provider.dimension):
                                logger.error(f"Invalid vector generated for chunk {chunk.id}. Skipping.")
                                continue
                                
                            # Prepare Qdrant Payload
                            payload = chunk.metadata_ or {}
                            payload.update({
                                "workspace_id": str(chunk.workspace_id),
                                "document_id": str(chunk.document_id),
                                "chunk_id": str(chunk.id),
                                "source": doc.source_id or doc.file_name or "Unknown",
                                "page_number": chunk.page_number or 0,
                                "section": chunk.section or "",
                                "document_type": doc.file_type or "unknown",
                                "tags": doc.tags or [],
                                "chunk_index": chunk.chunk_index,
                                "content": chunk.content,
                                "document_title": document_title
                            })
                            if agent_id:
                                payload["agent_id"] = agent_id
                            
                            points.append(
                                rest.PointStruct(
                                    id=str(chunk.id), # Map Qdrant ID to Chunk UUID
                                    vector=vector,
                                    payload=payload
                                )
                            )
                            
                            # Prepare Record
                            records_to_create.append(
                                EmbeddingRecord(
                                    workspace_id=chunk.workspace_id,
                                    document_id=chunk.document_id,
                                    chunk_id=chunk.id,
                                    provider=embedding_provider.name,
                                    model=getattr(embedding_provider, 'active_model', getattr(embedding_provider, 'model_name', 'unknown')),
                                    vector_dimension=embedding_provider.dimension,
                                    chunk_hash=chunk_hash
                                )
                            )

                    # 7. Upsert to Qdrant & Save Records
                    if points:
                        qdrant_service.upsert_vectors(workspace_id, points)
                        db.add_all(records_to_create)
                        await db.commit()
                        
                # 8. Complete Job
                await embedding_job_repo.update(db, db_obj=job, obj_in={
                    "status": EmbeddingJobStatus.COMPLETED,
                    "completed_at": datetime.utcnow()
                })
                
                # 9. Update Document Status to READY
                from app.models.knowledge import DocumentStatus
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.READY})
                    
                logger.info(f"Embedding job {job_id} completed successfully.")

            except Exception as e:
                logger.error(f"Embedding job {job_id} failed: {str(e)}")
                await db.rollback()
                await embedding_job_repo.update(db, db_obj=job, obj_in={
                    "status": EmbeddingJobStatus.FAILED,
                    "error_message": str(e)
                })
                from app.models.knowledge import DocumentStatus
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.FAILED})

    async def reembed_document(self, workspace_id: str, document_id: str):
        """
        Clears existing embeddings for a document and queues a new embedding job.
        """
        from app.models.vector import EmbeddingJobStatus
        from app.repositories.vector_repo import embedding_job_repo, embedding_record_repo, EmbeddingJobInternalCreate
        from app.services.vector.provider import embedding_provider
        from app.core.database import async_session_maker
        from app.tasks.knowledge_tasks import generate_embeddings_task

        async with async_session_maker() as db:
            # 1. Delete Qdrant vectors
            qdrant_service.delete_document_vectors(workspace_id, document_id)
            
            # 2. Delete existing EmbeddingRecords
            records = await embedding_record_repo.get_by_document(db, document_id)
            for record in records:
                await db.delete(record)
            await db.commit()
            
            # 3. Create new Job
            job_in = EmbeddingJobInternalCreate(
                workspace_id=workspace_id,
                document_id=document_id,
                provider=embedding_provider.name,
                status=EmbeddingJobStatus.PENDING
            )
            embedding_job = await embedding_job_repo.create(db, obj_in=job_in)
            
            # 4. Queue the task
            generate_embeddings_task.delay(str(embedding_job.id), workspace_id, document_id)
            
            return {"job_id": str(embedding_job.id), "status": "queued"}

embedding_service = EmbeddingService()
