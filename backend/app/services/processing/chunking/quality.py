import re

class ChunkQualityService:
    @staticmethod
    def score_chunk(content: str, token_count: int) -> float:
        """
        Calculates a quality score from 0.0 to 1.0 based on length, 
        information density, and structure.
        """
        if not content or token_count == 0:
            return 0.0
            
        score = 0.5  # Base score

        # 1. Length penalties
        if token_count < 20:
            score -= 0.3  # Too short
        elif token_count > 1000:
            score -= 0.2  # Too long, dilutes context
        else:
            score += 0.2  # Ideal range
            
        # 2. Information Density (alphanumeric ratio)
        alpha_count = len(re.findall(r'[a-zA-Z0-9]', content))
        if len(content) > 0:
            density = alpha_count / len(content)
            if density < 0.3:
                score -= 0.3  # Too much whitespace/symbols
            elif density > 0.6:
                score += 0.1
                
        # 3. Structural penalties
        if not re.search(r'[a-zA-Z]', content):
            score -= 0.4  # No letters
            
        return max(0.0, min(1.0, score))


class ChunkValidationService:
    @staticmethod
    def is_valid_chunk(content: str, token_count: int, min_tokens: int = 10) -> bool:
        """
        Validates whether a chunk should be saved to the vector database.
        Rejects empty, tiny, or corrupted chunks.
        """
        # Reject empty
        if not content or not content.strip():
            return False
            
        # Reject tiny
        if token_count < min_tokens:
            return False
            
        # Reject corrupted (mostly punctuation/whitespace)
        alpha_count = len(re.findall(r'[a-zA-Z0-9]', content))
        if len(content) > 0 and alpha_count / len(content) < 0.1:
            return False
            
        return True

chunk_quality_service = ChunkQualityService()
chunk_validation_service = ChunkValidationService()
