import pytest
import uuid
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_semantic_chunker():
    from app.services.processing.chunker import semantic_chunker
    
    text = "This is a test paragraph.\n\n" * 150 # Large text
    chunks = semantic_chunker.chunk_text(text, base_metadata={"source_type": "TXT"})
    
    assert len(chunks) > 0
    assert chunks[0].token_count <= 1000
    assert chunks[0].metadata["source_type"] == "TXT"
    assert "chunk_index" in chunks[0].metadata

@pytest.mark.asyncio
async def test_text_cleaner():
    from app.services.extractors.cleaner import TextCleaner
    
    dirty_text = "This \u200B is \xa0 some   messy \n\n\n text."
    cleaned = TextCleaner.clean(dirty_text)
    
    assert "  " not in cleaned
    assert "\n\n\n" not in cleaned
    assert cleaned == "This is some messy \n\n text."

@pytest.mark.asyncio
@patch('app.services.extractors.crawler.httpx.AsyncClient.get')
async def test_website_crawler(mock_get):
    from app.services.extractors.crawler import website_crawler
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><head><title>Test Title</title></head><body><nav>Menu</nav><p>Main content</p></body></html>"
    
    # We must patch raise_for_status out
    mock_response.raise_for_status = MagicMock()
    
    mock_get.return_value = mock_response
    
    results = await website_crawler.crawl("http://example.com")
    
    assert len(results) == 1
    assert results[0]["title"] == "Test Title"
    assert "Main content" in results[0]["content"]
    assert "Menu" not in results[0]["content"]

@pytest.mark.asyncio
@patch('app.services.vector.qdrant_service.qdrant_service.client')
async def test_qdrant_search(mock_qdrant_client):
    from app.services.vector.search_service import search_service
    from app.services.vector.provider import embedding_provider
    from app.models.vector import SearchEvent
    
    # Setup mock
    mock_hit = MagicMock()
    mock_hit.id = str(uuid.uuid4())
    mock_hit.score = 0.95
    mock_hit.payload = {"content": "Test match"}
    
    mock_results = MagicMock()
    mock_results.points = [mock_hit]
    
    mock_qdrant_client.query_points.return_value = mock_results
    
    # Patch embedding
    with patch.object(embedding_provider, 'embed_query', return_value=[0.1]*768):
        # We need a mock db session
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        
        # Avoid db actual calls by mocking the repo
        with patch('app.repositories.vector_repo.search_event_repo.create'):
            results = await search_service.semantic_search(
                db=mock_db,
                workspace_id=str(uuid.uuid4()),
                user_id=str(uuid.uuid4()),
                query="Find something"
            )
            
            assert len(results) == 1
            assert results[0]["score"] == 0.95
            assert results[0]["payload"]["content"] == "Test match"
