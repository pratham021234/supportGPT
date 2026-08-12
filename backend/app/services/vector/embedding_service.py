import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from qdrant_client.http import models as rest
from typing import List

from app.models.vector import EmbeddingJobStatus
from app.models.knowledge import DocumentChunk, Document
from app.repositories.vector_repo import embedding_job_repo
from app.services.vector.provider import embedding_provider
from app.services.vector.qdrant_service import qdrant_service
from app.core.database import async_session_maker

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

                # 5. Batch Embeddings (to handle limits)
                batch_size = 100
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i + batch_size]
                    
                    texts = [c.content for c in batch]
                    # Generate Embeddings
                    embeddings = await embedding_provider.embed_texts(texts)
                    
                    # 6. Format for Qdrant
                    points = []
                    for chunk, vector in zip(batch, embeddings):
                        # Construct rich payload
                        payload = chunk.metadata_ or {}
                        payload.update({
                            "chunk_id": str(chunk.id),
                            "workspace_id": str(chunk.workspace_id),
                            "document_id": str(chunk.document_id),
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

                    # 7. Upsert to Qdrant
                    qdrant_service.upsert_vectors(workspace_id, points)
                    
                # 8. Complete Job
                await embedding_job_repo.update(db, db_obj=job, obj_in={
                    "status": EmbeddingJobStatus.COMPLETED,
                    "completed_at": datetime.utcnow()
                })
                logger.info(f"Embedding job {job_id} completed successfully.")

            except Exception as e:
                logger.error(f"Embedding job {job_id} failed: {str(e)}")
                await db.rollback()
                await embedding_job_repo.update(db, db_obj=job, obj_in={
                    "status": EmbeddingJobStatus.FAILED,
                    "error_message": str(e)
                })

embedding_service = EmbeddingService()
