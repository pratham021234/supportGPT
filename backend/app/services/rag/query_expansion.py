import logging
from typing import List

logger = logging.getLogger(__name__)

class QueryExpansionService:
    def expand_query(self, query: str, keywords: List[str]) -> List[str]:
        """
        Expands the query with synonyms or alternative phrasing.
        For a production system without an LLM call here, we can do heuristic 
        expansion or just return the original keywords. Since the QueryProcessor
        already extracts keywords using an LLM, we'll assume they are decent, 
        and optionally we can add basic synonym maps if needed, or rely on 
        the LLM extraction as our primary expansion.
        """
        expanded = set(keywords)
        
        # Simple heuristic expansions for common support terms
        expansion_map = {
            "reset": ["recover", "change", "forgot"],
            "password": ["credentials", "login", "auth"],
            "refund": ["return", "money back", "cancel"],
            "api": ["integration", "developer", "webhook"],
            "error": ["bug", "issue", "fail", "broken"]
        }
        
        query_lower = query.lower()
        for term, synonyms in expansion_map.items():
            if term in query_lower:
                for syn in synonyms:
                    expanded.add(syn)
                    
        return list(expanded)

query_expansion_service = QueryExpansionService()
