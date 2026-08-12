import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks

from app.services.vector.qdrant_service import qdrant_service
from app.services.vector.batch_service import batch_embedding_service
from app.services.vector.provider import embedding_provider

logger = logging.getLogger(__name__)

class ReindexService:
    @classmethod
    async def rebuild_workspace_collection(cls, db: AsyncSession, workspace_id: str, background_tasks: BackgroundTasks) -> int:
        """
        Deletes the entire workspace collection and re-queues all documents for embedding.
        """
        collection_name = qdrant_service._get_collection_name(workspace_id)
        
        try:
            logger.warning(f"Rebuilding entire Qdrant collection for workspace {workspace_id}")
            qdrant_service.client.delete_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to delete collection during rebuild: {str(e)}")
            # Might not exist, which is fine
            pass
            
        # Ensure it exists empty
        qdrant_service.ensure_collection(workspace_id, embedding_provider.dimension)
        
        # Queue all docs
        queued = await batch_embedding_service.queue_workspace_reindex(db, workspace_id, background_tasks)
        return queued

reindex_service = ReindexService()
