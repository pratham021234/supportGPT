import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import re

from app.services.vector.search_service import search_service
from app.services.vector.provider import embedding_provider
from app.services.vector.qdrant_service import qdrant_service
from qdrant_client.http import models as rest
from app.services.rag.context_ranking import context_ranking_service

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        # Weighting for our hybrid scoring simulation
        self.vector_weight = 0.7
        self.keyword_weight = 0.3

    def _calculate_keyword_score(self, content: str, keywords: List[str]) -> float:
        """Simulates BM25 locally by counting keyword term frequency in content."""
        if not keywords or not content:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        for kw in keywords:
            kw = kw.lower()
            # Count occurrences
            matches = len(re.findall(r'\b' + re.escape(kw) + r'\b', content_lower))
            if matches > 0:
                # Diminishing returns for multiple matches (log-like behavior)
                score += (1.0 - (0.5 ** matches))
                
        # Normalize roughly by max possible score (1.0 per keyword)
        max_score = len(keywords)
        return score / max_score if max_score > 0 else 0.0

    async def retrieve(
        self,
        db: AsyncSession,
        workspace_id: str,
        user_id: Optional[str],
        query: str,
        keywords: List[str],
        limit: int = 10,
        agent_routing: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes a hybrid retrieval merging Vector + Keyword scores.
        """
        # 1. Embed Query
        query_vector = await embedding_provider.embed_query(query)
        
        # 2. Build metadata filters
        filter_must = []
        if agent_routing:
            # We map this directly to the agent_id payload using the exact match.
            # In Phase B4 we added agent_id to Qdrant.
            filter_must.append(
                rest.FieldCondition(
                    key="agent_id",
                    match=rest.MatchValue(value=agent_routing)
                )
            )
            
        query_filter = rest.Filter(must=filter_must) if filter_must else None
        
        # 3. Fetch 2x limit from Qdrant for reranking
        collection_name = qdrant_service._get_collection_name(workspace_id)
        try:
            results = qdrant_service.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit * 2
            )
            raw_hits = results.points
        except Exception as e:
            logger.error(f"Search failed for {collection_name}: {e}")
            raw_hits = []

        # 4. Rerank using Keyword + Vector (Hybrid)
        hybrid_results = []
        for hit in raw_hits:
            vector_score = hit.score
            content = hit.payload.get("content", "")
            kw_score = self._calculate_keyword_score(content, keywords)
            
            final_score = (vector_score * self.vector_weight) + (kw_score * self.keyword_weight)
            
            hybrid_results.append({
                "id": hit.id,
                "score": final_score, # Use hybrid score
                "vector_score": vector_score,
                "keyword_score": kw_score,
                "payload": hit.payload
            })
            
        # 5. Advanced Context Ranking (Phase B5)
        top_results = context_ranking_service.rank_context(hybrid_results, agent_routing or "GLOBAL")[:limit]
        
        return top_results

retrieval_engine = RetrievalService()
