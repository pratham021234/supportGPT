import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.services.vector.qdrant_service import qdrant_service
from app.repositories.knowledge_repo import document_repo

logger = logging.getLogger(__name__)

class VectorCleanupService:
    @classmethod
    async def cleanup_orphan_document_vectors(cls, db: AsyncSession, workspace_id: str, document_id: str):
        """
        Deletes all vectors associated with a document_id.
        Use this after a document is deleted from Postgres or during a rebuild.
        """
        try:
            logger.info(f"Scrubbing vectors for document {document_id} in workspace {workspace_id}")
            qdrant_service.delete_document_vectors(workspace_id, document_id)
        except Exception as e:
            logger.error(f"Failed to scrub vectors for document {document_id}: {str(e)}")
            raise e

vector_cleanup_service = VectorCleanupService()
