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

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Uses OpenAI models for embedding generation."""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self._dimension = 1536 # Default for text-embedding-3-small
        
    @property
    def dimension(self) -> int:
        return self._dimension
        
    @property
    def name(self) -> str:
        return "OPENAI"
        
    def _is_configured(self):
        return bool(settings.OPENAI_API_KEY)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self._is_configured():
            logger.warning("OpenAI API Key missing. Falling back to Mock embeddings.")
            return await MockEmbeddingProvider(self.dimension).embed_texts(texts)
            
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # OpenAI handles batching of strings directly in the API call
            response = await client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            
            # Sort by index just to be safe
            embeddings = [data.embedding for data in sorted(response.data, key=lambda x: x.index)]
            return embeddings
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {str(e)}")
            raise e

    async def embed_query(self, query: str) -> List[float]:
        if not self._is_configured():
            return await MockEmbeddingProvider(self.dimension).embed_query(query)
            
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = await client.embeddings.create(
                input=query,
                model=self.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI query embedding failed: {str(e)}")
            raise e

class MultiProviderEmbeddingOrchestrator(BaseEmbeddingProvider):
    """Orchestrates fallback between multiple providers."""
    def __init__(self):
        self.providers = []
        if settings.GEMINI_API_KEY:
            self.providers.append(GeminiEmbeddingProvider())
        if getattr(settings, "OPENAI_API_KEY", None):
            self.providers.append(OpenAIEmbeddingProvider())
        if not self.providers:
            self.providers.append(MockEmbeddingProvider())
            
        self.primary_provider = self.providers[0]

    @property
    def dimension(self) -> int:
        return self.primary_provider.dimension
        
    @property
    def name(self) -> str:
        return self.primary_provider.name
        
    @property
    def active_model(self) -> str:
        if hasattr(self.primary_provider, "model_name"):
            return self.primary_provider.model_name
        return "mock-model"

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        last_exception = None
        for provider in self.providers:
            try:
                return await provider.embed_texts(texts)
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}. Trying fallback.")
                last_exception = e
        raise last_exception or Exception("All embedding providers failed.")

    async def embed_query(self, query: str) -> List[float]:
        last_exception = None
        for provider in self.providers:
            try:
                return await provider.embed_query(query)
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}. Trying fallback.")
                last_exception = e
        raise last_exception or Exception("All embedding providers failed.")

# Dependency Injection approach
def get_embedding_provider() -> MultiProviderEmbeddingOrchestrator:
    return MultiProviderEmbeddingOrchestrator()

embedding_provider = get_embedding_provider()
