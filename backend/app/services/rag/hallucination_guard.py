import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HallucinationGuard:
    def check_hallucinations(
        self,
        answer: str,
        citations_count: int,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Validates whether the answer is a hallucination.
        Returns True if hallucination is detected (should escalate or warn), False if safe.
        
        Rules:
        No Source -> No Answer -> Escalate
        Low Context -> Escalate
        Missing Information -> Admit Unknown
        """
        # 1. No Sources but an answer was given (and it's not the "I could not find" fallback)
        unknown_phrases = ["could not find", "i don't know", "i cannot find", "unable to find"]
        is_unknown_fallback = any(phrase in answer.lower() for phrase in unknown_phrases)
        
        if citations_count == 0 and not is_unknown_fallback and len(answer) > 50:
            logger.warning("Hallucination Guard: Answer provided without citations.")
            return True
            
        # 2. Low Context
        if not retrieved_chunks:
            logger.info("Hallucination Guard: No context was provided to the LLM. Escalating.")
            return True
            
        return False

hallucination_guard = HallucinationGuard()
