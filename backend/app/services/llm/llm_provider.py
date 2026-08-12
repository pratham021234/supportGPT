from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured_answer(self, prompt: str, context: str, query: str) -> Dict[str, Any]:
        """
        Generates an answer using the provided LLM.
        Should return a dictionary matching AnswerOutput structure:
        {
            "answer": str,
            "citations": [{"chunk_id": str, "claim": str}],
            "confidence_score": float
        }
        """
        pass
