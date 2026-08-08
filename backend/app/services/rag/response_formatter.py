from typing import Dict, Any, List
import logging
from app.services.rag.state import Citation

logger = logging.getLogger(__name__)

class ResponseFormatter:
    def format_final_response(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes the RAG state into a standard JSON response for the client.
        """
        citations: List[Citation] = state_dict.get("citations", [])
        
        # Deduplicate sources for a clean list
        unique_sources = []
        seen = set()
        for cit in citations:
            doc_title = getattr(cit, 'document_title', 'Unknown Document')
            if doc_title not in seen:
                seen.add(doc_title)
                unique_sources.append(doc_title)
        
        return {
            "answer": state_dict.get("answer", ""),
            "confidence": state_dict.get("confidence_score", 0.0),
            "escalate": state_dict.get("escalate", False),
            "sources": unique_sources,
            "citations": [
                {
                    "chunk_id": c.chunk_id,
                    "claim": c.claim,
                    "document_title": getattr(c, 'document_title', None)
                } for c in citations
            ],
            "metadata": {
                "latency_ms": state_dict.get("latency_ms", 0),
                "language": state_dict.get("language", "en"),
                "intent": state_dict.get("query_type", "GENERAL")
            }
        }

response_formatter = ResponseFormatter()
