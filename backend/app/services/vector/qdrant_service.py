import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        # Default to memory for dev if no URL provided
        if settings.QDRANT_URL == ":memory:":
            self.client = QdrantClient(":memory:")
        else:
            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    def _get_collection_name(self, workspace_id: str) -> str:
        return f"supportgpt_workspace_{workspace_id.replace('-', '_')}"

    def ensure_collection(self, workspace_id: str, vector_size: int):
        """Ensures that a collection exists for a workspace."""
        collection_name = self._get_collection_name(workspace_id)
        
        try:
            self.client.get_collection(collection_name=collection_name)
        except (UnexpectedResponse, ValueError): # ValueError is sometimes raised by local mode
            # Collection does not exist, create it
            logger.info(f"Creating Qdrant collection: {collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=rest.VectorParams(
                    size=vector_size,
                    distance=rest.Distance.COSINE
                )
            )
            # Create payload indices for fast filtering
            self.client.create_payload_index(collection_name, "document_id", field_schema="keyword")
            self.client.create_payload_index(collection_name, "source_type", field_schema="keyword")
            self.client.create_payload_index(collection_name, "language", field_schema="keyword")
            self.client.create_payload_index(collection_name, "agent_id", field_schema="keyword")

    def upsert_vectors(self, workspace_id: str, points: List[rest.PointStruct]):
        """Upserts a list of vectors to the workspace's collection."""
        if not points:
            return
            
        collection_name = self._get_collection_name(workspace_id)
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    def delete_document_vectors(self, workspace_id: str, document_id: str):
        """Deletes all vectors belonging to a specific document."""
        collection_name = self._get_collection_name(workspace_id)
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=rest.FilterSelector(
                    filter=rest.Filter(
                        must=[
                            rest.FieldCondition(
                                key="document_id",
                                match=rest.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
        except (UnexpectedResponse, ValueError) as e:
            logger.error(f"Failed to delete document vectors: {e}")

    def search(
        self, 
        workspace_id: str, 
        query_vector: List[float], 
        limit: int = 10,
        document_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> List[Any]:
        """
        Performs a semantic search on a workspace collection.
        Optionally filters by document_id and agent_id for strict isolation.
        """
        collection_name = self._get_collection_name(workspace_id)
        
        filter_must = []
        if document_id:
            filter_must.append(
                rest.FieldCondition(
                    key="document_id",
                    match=rest.MatchValue(value=document_id)
                )
            )
            
        if agent_id:
            # Vectors belong either to no agent (global workspace) OR the specific agent
            # For strict isolation: if agent_id is provided, limit search to that agent + global
            # For this MVP: exact match on agent_id
            filter_must.append(
                rest.FieldCondition(
                    key="agent_id",
                    match=rest.MatchValue(value=agent_id)
                )
            )
            
        query_filter = rest.Filter(must=filter_must) if filter_must else None
        
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit
            )
            return results.points
        except (UnexpectedResponse, ValueError) as e:
            logger.error(f"Search failed for {collection_name}: {e}")
            return []

    def get_collection_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Returns stats about the collection."""
        collection_name = self._get_collection_name(workspace_id)
        try:
            info = self.client.get_collection(collection_name)
            return {
                "status": str(info.status),
                "vectors_count": info.points_count
            }
        except (UnexpectedResponse, ValueError):
            return {"status": "MISSING", "vectors_count": 0}

qdrant_service = QdrantService()
