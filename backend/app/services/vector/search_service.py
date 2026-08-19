import logging
from typing import List, Dict, Any, Optional
import time
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.vector.provider import embedding_provider
from app.services.vector.qdrant_service import qdrant_service
from app.models.vector import SearchEvent
from app.repositories.vector_repo import search_event_repo, SearchEventInternalCreate

logger = logging.getLogger(__name__)

class RankingService:
    @staticmethod
    def rrf_score(rank: int, k: int = 60) -> float:
        """Calculates the Reciprocal Rank Fusion score."""
        return 1.0 / (k + rank)

    @classmethod
    def fuse_results(cls, semantic_results: List[Any], keyword_results: List[Any]) -> List[Any]:
        """Combines semantic and keyword results using RRF."""
        scores = {}
        items = {}
        
        for rank, item in enumerate(semantic_results):
            scores[item.id] = scores.get(item.id, 0) + cls.rrf_score(rank)
            items[item.id] = item
            
        for rank, item in enumerate(keyword_results):
            scores[item.id] = scores.get(item.id, 0) + cls.rrf_score(rank)
            items[item.id] = item
            
        # Sort by combined RRF score descending
        fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        result_list = []
        for item_id, combined_score in fused:
            item = items[item_id]
            # Override Qdrant score with RRF combined score
            item.score = combined_score
            result_list.append(item)
            
        return result_list

class SearchService:
    def _format_citation(self, hit: Any) -> Dict[str, Any]:
        """Formats the payload into a standard Citation dictionary."""
        payload = hit.payload or {}
        return {
            "chunk": payload.get("content", ""),
            "source": payload.get("source", "Unknown"),
            "page": payload.get("page_number", 0),
            "section": payload.get("section", ""),
            "score": hit.score,
            "document_id": payload.get("document_id"),
            "chunk_id": payload.get("chunk_id")
        }

    async def semantic_search(
        self,
        db: AsyncSession,
        workspace_id: str,
        user_id: Optional[str],
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Executes a dense vector semantic search."""
        start_time = time.time()
        try:
            query_vector = await embedding_provider.embed_query(query)
            
            results = qdrant_service.search(
                workspace_id=workspace_id,
                query_vector=query_vector,
                limit=limit,
                filters=filters
            )
            
            formatted_results = [self._format_citation(hit) for hit in results]
            
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_event(db, workspace_id, user_id, query, "SEMANTIC", len(formatted_results), latency_ms)
            return formatted_results
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_event(db, workspace_id, user_id, query, "SEMANTIC_ERROR", 0, latency_ms)
            raise e

    async def hybrid_search(
        self,
        db: AsyncSession,
        workspace_id: str,
        user_id: Optional[str],
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Executes both dense and keyword search, fusing results via RRF."""
        start_time = time.time()
        try:
            # 1. Semantic Search
            query_vector = await embedding_provider.embed_query(query)
            semantic_results = qdrant_service.search(
                workspace_id=workspace_id,
                query_vector=query_vector,
                limit=limit * 2, # Fetch more for better fusion overlap
                filters=filters
            )
            
            # 2. Keyword Search
            keyword_results = qdrant_service.search(
                workspace_id=workspace_id,
                query_text=query,
                limit=limit * 2,
                filters=filters
            )
            
            # 3. Rank & Fuse
            fused_results = RankingService.fuse_results(semantic_results, keyword_results)
            top_results = fused_results[:limit]
            
            # 4. Format
            formatted_results = [self._format_citation(hit) for hit in top_results]
            
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_event(db, workspace_id, user_id, query, "HYBRID", len(formatted_results), latency_ms)
            return formatted_results
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_event(db, workspace_id, user_id, query, "HYBRID_ERROR", 0, latency_ms)
            raise e

    async def _log_event(self, db, workspace_id, user_id, query, s_type, count, latency):
        try:
            event_in = SearchEventInternalCreate(
                workspace_id=workspace_id,
                user_id=user_id,
                query=query,
                search_type=s_type,
                results_count=count,
                latency_ms=latency
            )
            await search_event_repo.create(db, obj_in=event_in)
        except Exception as e:
            logger.warning(f"Failed to log search event: {e}")

search_service = SearchService()
