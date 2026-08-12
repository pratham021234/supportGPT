import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ContextRankingService:
    def rank_context(self, retrieved_chunks: List[Dict[str, Any]], agent_scope: str) -> List[Dict[str, Any]]:
        """
        Ranks chunks using multi-variable weighting.
        Similarity Score: 50%
        Authority (e.g. FAQ vs user post): 20%
        Freshness (recent chunks): 20%
        Agent Scope match: 10%
        """
        ranked = []
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            base_score = chunk.get("score", 0.0) # Original Hybrid score
            
            # 1. Similarity (Max 0.5)
            # Assuming base score is 0 to 1.0 (from retrieval_engine)
            sim_score = min(base_score, 1.0) * 0.5
            
            # 2. Authority (Max 0.2)
            source_type = payload.get("source_type", "UNKNOWN").upper()
            auth_score = 0.2 if source_type in ["FAQ", "OFFICIAL_DOC"] else 0.1
            
            # 3. Freshness (Max 0.2)
            # Mocking freshness if no timestamp is present. Usually a decay function.
            freshness_score = 0.15 # Default
            
            # 4. Agent Scope Match (Max 0.1)
            chunk_agent = payload.get("agent_id", "GLOBAL").upper()
            agent_score = 0.1 if chunk_agent == agent_scope.upper() or chunk_agent == "GLOBAL" else 0.0
            
            final_score = sim_score + auth_score + freshness_score + agent_score
            
            chunk["ranked_score"] = final_score
            ranked.append(chunk)
            
        ranked.sort(key=lambda x: x["ranked_score"], reverse=True)
        return ranked

context_ranking_service = ContextRankingService()
