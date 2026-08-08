import logging
from typing import List, Dict, Any
from app.services.rag.state import Citation

logger = logging.getLogger(__name__)

class CitationService:
    def validate_citations(self, citations: List[Citation], retrieved_chunks: List[Dict[str, Any]]) -> List[Citation]:
        """
        Validates citations provided by the LLM against the actual retrieved chunks.
        Removes hallucinated citations and enriches valid ones with accurate document names.
        """
        valid_citations = []
        
        # Build a lookup map of retrieved chunks
        chunk_lookup = {}
        for hit in retrieved_chunks:
            payload = hit.get("payload", {})
            chunk_id = payload.get("chunk_id", hit.get("id"))
            chunk_lookup[str(chunk_id)] = payload
            
        for cit in citations:
            chunk_id_str = str(cit.chunk_id).strip()
            
            if chunk_id_str in chunk_lookup:
                # Valid citation
                payload = chunk_lookup[chunk_id_str]
                cit.document_title = payload.get("document_title", cit.document_title or "Unknown Document")
                
                # Optional: ensure we don't have exact duplicates
                if not any(c.chunk_id == cit.chunk_id and c.claim == cit.claim for c in valid_citations):
                    valid_citations.append(cit)
            else:
                logger.warning(f"Hallucinated citation removed: {chunk_id_str}")
                
        return valid_citations

citation_service = CitationService()
