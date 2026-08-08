import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self, default_threshold: float = 70.0):
        self.default_threshold = default_threshold

    def evaluate(
        self,
        confidence_score: float,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Determines if a query should be escalated to a human.
        """
        # 1. Low Confidence Trigger
        if confidence_score < self.default_threshold:
            logger.info(f"Escalation triggered: Confidence {confidence_score} < {self.default_threshold}")
            return True
            
        # 2. Missing Knowledge Trigger
        if not retrieved_chunks:
            logger.info("Escalation triggered: No knowledge base chunks found.")
            return True
            
        # 3. Explicit Customer Request (Naive check, could be LLM intent)
        explicit_triggers = ["talk to a human", "customer service", "agent", "real person", "escalate"]
        query_lower = query.lower()
        if any(trigger in query_lower for trigger in explicit_triggers):
            logger.info("Escalation triggered: Explicit human request detected in query.")
            return True
            
        return False

escalation_service = EscalationService()
