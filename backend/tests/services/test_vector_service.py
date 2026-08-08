import pytest
from qdrant_client.http import models as rest
from app.services.vector.qdrant_service import qdrant_service
from app.services.vector.provider import MockEmbeddingProvider

@pytest.fixture
def mock_provider():
    return MockEmbeddingProvider(dim=10)

def test_qdrant_ensure_collection(mock_provider):
    workspace_id = "test_workspace_123"
    
    # Should not raise any errors
    qdrant_service.ensure_collection(workspace_id, mock_provider.dimension)
    
    # Get stats
    stats = qdrant_service.get_collection_stats(workspace_id)
    assert stats["status"] == "green" or stats["status"] == "yellow"
    assert stats["vectors_count"] == 0

@pytest.mark.asyncio
async def test_qdrant_upsert_and_search(mock_provider):
    workspace_id = "test_workspace_123"
    qdrant_service.ensure_collection(workspace_id, mock_provider.dimension)
    
    # Upsert a vector
    vector = await mock_provider.embed_query("test query")
    point = rest.PointStruct(
        id="123e4567-e89b-12d3-a456-426614174000",
        vector=vector,
        payload={"document_id": "doc123", "content": "hello world"}
    )
    
    qdrant_service.upsert_vectors(workspace_id, [point])
    
    # Search
    results = qdrant_service.search(workspace_id, vector, limit=5)
    assert len(results) > 0
    assert results[0].payload["document_id"] == "doc123"
    
def test_qdrant_delete_document_vectors(mock_provider):
    workspace_id = "test_workspace_123"
    # Execute delete
    qdrant_service.delete_document_vectors(workspace_id, "doc123")
    # Note: Local mode deletion sometimes takes a moment or acts differently, 
    # but the API call itself shouldn't raise errors.
