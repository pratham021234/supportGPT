import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
from unittest.mock import MagicMock
sys.modules['qdrant_client'] = MagicMock()
sys.modules['qdrant_client.http'] = MagicMock()
sys.modules['qdrant_client.http.models'] = MagicMock()
sys.modules['qdrant_client.http.exceptions'] = MagicMock()

import app.core.config
app.core.config.settings.OPENAI_API_KEY = "test"
app.core.config.settings.GEMINI_API_KEY = "test"

from app.services.vector.embedding_service import embedding_service
from app.services.vector.provider import embedding_provider, OpenAIEmbeddingProvider, MockEmbeddingProvider
from app.services.vector.cache_service import embedding_cache_service
from app.services.vector.validation_service import embedding_validation_service

@pytest.fixture
def mock_db():
    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def execute(self, query):
            mock_result = MagicMock()
            mock_result.scalars().all.return_value = []
            return mock_result
        def add_all(self, objs):
            pass
        async def commit(self):
            pass
        async def rollback(self):
            pass
        async def delete(self, obj):
            pass
    return MockSession()

@pytest.mark.asyncio
async def test_cache_hashing():
    text1 = "This is a test chunk."
    text2 = "This is a test chunk. "
    
    hash1 = embedding_cache_service.compute_hash(text1)
    hash2 = embedding_cache_service.compute_hash(text2)
    
    assert hash1 == hash2

def test_validation_service():
    # Valid
    assert embedding_validation_service.is_valid_vector([0.1, 0.2, 0.3], 3) == True
    
    # Invalid length
    assert embedding_validation_service.is_valid_vector([0.1, 0.2], 3) == False
    
    # Invalid nulls
    assert embedding_validation_service.is_valid_vector([], 3) == False
    
    # All zeros
    assert embedding_validation_service.is_valid_vector([0.0, 0.0, 0.0], 3) == False
    
    # NaN
    assert embedding_validation_service.is_valid_vector([0.1, float('nan'), 0.3], 3) == False

@pytest.mark.asyncio
async def test_openai_fallback():
    provider = OpenAIEmbeddingProvider()
    
    # Unconfigured fallback
    with patch.object(provider, "_is_configured", return_value=False):
        embeddings = await provider.embed_texts(["test"])
        assert len(embeddings) == 1
        assert len(embeddings[0]) == provider.dimension

@pytest.mark.asyncio
@patch("app.services.vector.embedding_service.embedding_job_repo.get")
@patch("app.services.vector.embedding_service.document_repo.get")
@patch("app.services.vector.embedding_service.async_session_maker")
async def test_process_empty_chunks(mock_session_maker, mock_doc_get, mock_job_get, mock_db):
    mock_session_maker.return_value = mock_db
    mock_job = MagicMock()
    mock_job_get.return_value = mock_job
    
    mock_doc = MagicMock()
    mock_doc.title = "Test Doc"
    mock_doc_get.return_value = mock_doc
    
    # Process
    await embedding_service.process_document_embeddings("job_123", "ws_123", "doc_123")
    
    # Job should be marked completed
    assert mock_job.status == "COMPLETED"
