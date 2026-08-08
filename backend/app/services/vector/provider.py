import random
import logging
from abc import ABC, abstractmethod
from typing import List
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseEmbeddingProvider(ABC):
    """Abstract base class for generating vector embeddings."""
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass
        
    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        pass

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """A mock provider for testing or local dev without API keys."""
    
    def __init__(self, dim: int = 768):
        self._dimension = dim
        
    @property
    def dimension(self) -> int:
        return self._dimension
        
    @property
    def name(self) -> str:
        return "MOCK"

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Generate random deterministically length-matched float arrays
        return [[random.uniform(-1.0, 1.0) for _ in range(self.dimension)] for _ in texts]
        
    async def embed_query(self, query: str) -> List[float]:
        return [random.uniform(-1.0, 1.0) for _ in range(self.dimension)]

class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Uses Google's Gemini models for embedding generation."""
    
    def __init__(self, model_name: str = "models/text-embedding-004"):
        self.model_name = model_name
        self._dimension = 768 # Default for text-embedding-004
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
    @property
    def dimension(self) -> int:
        return self._dimension
        
    @property
    def name(self) -> str:
        return "GEMINI"
        
    def _is_configured(self):
        return bool(settings.GEMINI_API_KEY)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self._is_configured():
            logger.warning("Gemini API Key missing. Falling back to Mock embeddings.")
            return await MockEmbeddingProvider(self.dimension).embed_texts(texts)
            
        try:
            # google-generativeai API allows batch embedding via passing a list
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Gemini embedding failed: {str(e)}")
            raise e

    async def embed_query(self, query: str) -> List[float]:
        if not self._is_configured():
            return await MockEmbeddingProvider(self.dimension).embed_query(query)
            
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Gemini query embedding failed: {str(e)}")
            raise e

# Factory or Dependency Injection approach
def get_embedding_provider() -> BaseEmbeddingProvider:
    if settings.GEMINI_API_KEY:
        return GeminiEmbeddingProvider()
    return MockEmbeddingProvider()

embedding_provider = get_embedding_provider()
