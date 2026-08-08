import logging
from typing import List, Dict, Any, Optional
import time
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.vector.provider import embedding_provider
from app.services.vector.qdrant_service import qdrant_service
from app.models.vector import SearchEvent
from app.repositories.vector_repo import search_event_repo, SearchEventInternalCreate

logger = logging.getLogger(__name__)

class SearchService:
    async def semantic_search(
        self,
        db: AsyncSession,
        workspace_id: str,
        user_id: Optional[str],
        query: str,
        limit: int = 10,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes a semantic search against the workspace's vector collection.
        Tracks the search event for analytics.
        """
        start_time = time.time()
        
        try:
            # 1. Embed Query
            query_vector = await embedding_provider.embed_query(query)
            
            # 2. Search Qdrant
            results = qdrant_service.search(
                workspace_id=workspace_id,
                query_vector=query_vector,
                limit=limit,
                document_id=document_id
            )
            
            # 3. Format Results
            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
                
            latency_ms = int((time.time() - start_time) * 1000)
            
            # 4. Log Analytics Event
            event_in = SearchEventInternalCreate(
                workspace_id=workspace_id,
                user_id=user_id,
                query=query,
                search_type="SEMANTIC",
                results_count=len(formatted_results),
                latency_ms=latency_ms
            )
            await search_event_repo.create(db, obj_in=event_in)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic search failed for workspace {workspace_id}: {e}")
            # Still attempt to log the failure
            latency_ms = int((time.time() - start_time) * 1000)
            event_in = SearchEventInternalCreate(
                workspace_id=workspace_id,
                user_id=user_id,
                query=query,
                search_type="SEMANTIC_ERROR",
                results_count=0,
                latency_ms=latency_ms
            )
            await search_event_repo.create(db, obj_in=event_in)
            raise e

search_service = SearchService()
