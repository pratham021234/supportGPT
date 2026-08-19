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
            
            # Create Text index for BM25 (Hybrid search)
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="content",
                field_schema=rest.TextIndexParams(
                    type="text",
                    tokenizer=rest.TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=15,
                    lowercase=True,
                )
            )

    def delete_workspace_collection(self, workspace_id: str):
        """Deletes a workspace collection completely."""
        collection_name = self._get_collection_name(workspace_id)
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted Qdrant collection: {collection_name}")
        except (UnexpectedResponse, ValueError) as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")

    def rebuild_collection(self, workspace_id: str, vector_size: int):
        """Drops and recreates the workspace collection."""
        self.delete_workspace_collection(workspace_id)
        self.ensure_collection(workspace_id, vector_size)

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
        query_vector: Optional[List[float]] = None,
        query_text: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Performs a semantic, keyword, or hybrid search on a workspace collection.
        filters expects a dictionary like: {"document_id": "...", "agent_id": "...", "tags": ["..."]}
        """
        collection_name = self._get_collection_name(workspace_id)
        
        filter_must = []
        if filters:
            for key, value in filters.items():
                if value is None:
                    continue
                if isinstance(value, list):
                    # Any match within the list
                    filter_must.append(
                        rest.FieldCondition(
                            key=key,
                            match=rest.MatchAny(any=value)
                        )
                    )
                else:
                    filter_must.append(
                        rest.FieldCondition(
                            key=key,
                            match=rest.MatchValue(value=value)
                        )
                    )
        
        # If keyword search is provided, we add a MatchText to the filter
        if query_text:
            filter_must.append(
                rest.FieldCondition(
                    key="content",
                    match=rest.MatchText(text=query_text)
                )
            )
            
        query_filter = rest.Filter(must=filter_must) if filter_must else None
        
        try:
            if query_vector:
                # Semantic search (or Hybrid if query_text was added to filter)
                results = self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    query_filter=query_filter,
                    limit=limit
                )
                return results.points
            elif query_filter:
                # Keyword only search
                results, _ = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                # Mock scores for keyword search since scroll doesn't score
                for i, r in enumerate(results):
                    r.score = 1.0 / (i + 1)
                return results
            else:
                return []
                
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
