import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ConfidenceEngine:
    def calculate_confidence(
        self,
        llm_confidence: float,
        retrieved_chunks: List[Dict[str, Any]],
        citations_count: int
    ) -> float:
        """
        Calculates a final confidence score (0-100) using heuristics:
        - The base is the LLM's self-reported certainty.
        - We penalize if retrieval quality is low.
        - We penalize if citations are missing.
        """
        if not retrieved_chunks:
            # If no context, confidence must be zero because of anti-hallucination rule
            return 0.0

        # Calculate retrieval quality (avg score of top 3 chunks)
        top_k = retrieved_chunks[:3]
        avg_retrieval_score = sum(hit.get("score", 0.0) for hit in top_k) / len(top_k)
        
        # Normalize retrieval score assuming max is roughly 1.0 (vector max) + 1.0 (keyword max) = 2.0
        # Wait, pure cosine vector is 0 to 1. Keyword was 0 to 1. Hybrid max is 1.0 because of weights (0.7 + 0.3)
        # So avg_retrieval_score should be between 0.0 and 1.0
        retrieval_factor = min(avg_retrieval_score, 1.0)
        
        # Citation factor: we expect at least 1 citation if the LLM provided an answer
        citation_factor = 1.0 if citations_count > 0 else 0.5
        
        # Combine heuristics
        # 60% LLM certainty, 30% Retrieval Quality, 10% Citation presence
        final_score = (llm_confidence * 0.6) + ((retrieval_factor * 100) * 0.3) + (100 * citation_factor * 0.1)
        
        # Cap between 0 and 100
        final_score = max(0.0, min(100.0, final_score))
        
        logger.info(f"Calculated Confidence: {final_score:.2f} (LLM: {llm_confidence}, Retrieval: {retrieval_factor:.2f}, Cits: {citations_count})")
        return round(final_score, 2)

confidence_engine = ConfidenceEngine()
