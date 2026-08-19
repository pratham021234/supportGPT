import logging
from typing import List
import math

logger = logging.getLogger(__name__)

class EmbeddingValidationService:
    def is_valid_vector(self, vector: List[float], expected_dimension: int) -> bool:
        """Validates a single vector's structural integrity."""
        if not vector:
            logger.error("Vector is empty or null.")
            return False
            
        if len(vector) != expected_dimension:
            logger.error(f"Vector dimension mismatch. Expected {expected_dimension}, got {len(vector)}.")
            return False
            
        # Check for NaN, Inf, or all zeros
        is_all_zero = True
        for val in vector:
            if math.isnan(val) or math.isinf(val):
                logger.error("Vector contains NaN or Inf.")
                return False
            if val != 0.0:
                is_all_zero = False
                
        if is_all_zero:
            logger.error("Vector is entirely zeros.")
            return False
            
        return True

embedding_validation_service = EmbeddingValidationService()
