import logging
from typing import Dict, Any

from app.services.vector.qdrant_service import qdrant_service
from app.services.vector.provider import embedding_provider

logger = logging.getLogger(__name__)

class VectorHealthService:
    @classmethod
    def get_cluster_health(cls) -> Dict[str, Any]:
        """
        Returns cluster-wide health status and provider configuration.
        """
        try:
            # Check basic provider state
            provider_name = embedding_provider.name
            provider_dim = embedding_provider.dimension
            
            # Check Qdrant state (by creating/dropping a dummy collection or just checking cluster)
            # qdrant_client exposes cluster info if requested
            # For simplicity, we just ping the collections list
            collections = qdrant_service.client.get_collections()
            
            return {
                "status": "healthy",
                "provider": provider_name,
                "dimension": provider_dim,
                "collections_count": len(collections.collections) if collections else 0,
                "qdrant_available": True
            }
        except Exception as e:
            logger.error(f"Vector cluster health check failed: {str(e)}")
            return {
                "status": "degraded",
                "provider": embedding_provider.name,
                "qdrant_available": False,
                "error": str(e)
            }

vector_health_service = VectorHealthService()
