import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_query_processor():
    from app.services.rag.query_processor import query_processor
    
    # Mocking LLM
    with patch.object(query_processor, 'llm', new_callable=MagicMock) as mock_llm:
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "normalized_query": "how do i reset my password",
            "intent": "SUPPORT",
            "language": "en",
            "keywords": ["reset", "password"],
            "agent_routing": "TECHNICAL"
        }
        
        # We need to mock the chain invoke
        mock_chain = MagicMock()
        mock_chain.ainvoke.return_value = mock_result
        query_processor.prompt.__or__ = MagicMock(return_value=mock_chain)
        
        result = await query_processor.process_query("How do I reset my password?   ")
        
        assert result["intent"] == "SUPPORT"
        assert result["language"] == "en"
        assert result["agent_routing"] == "TECHNICAL"
        assert "password" in result["keywords"]

@pytest.mark.asyncio
async def test_retrieval_engine():
    from app.services.rag.retrieval_engine import retrieval_engine
    from app.services.vector.qdrant_service import qdrant_service
    from app.services.vector.provider import embedding_provider
    
    with patch.object(qdrant_service.client, 'query_points') as mock_query:
        mock_hit = MagicMock()
        mock_hit.id = "123"
        mock_hit.score = 0.8
        mock_hit.payload = {"content": "You can reset your password in settings."}
        
        mock_results = MagicMock()
        mock_results.points = [mock_hit]
        mock_query.return_value = mock_results
        
        with patch.object(embedding_provider, 'embed_query', return_value=[0.1]*768):
            results = await retrieval_engine.retrieve(
                db=MagicMock(),
                workspace_id="test_workspace",
                user_id="user1",
                query="reset password",
                keywords=["reset", "password"],
                limit=10
            )
            
            assert len(results) == 1
            # 0.8 * 0.7 (vector_weight) + (approx 1.0) * 0.3 (keyword_weight)
            assert results[0]["score"] > 0.5
            assert results[0]["id"] == "123"

def test_context_assembler():
    from app.services.rag.context_assembler import context_assembler
    
    chunks = [
        {"id": "1", "payload": {"chunk_id": "1", "document_title": "Doc A", "content": "Hello"}},
        {"id": "1", "payload": {"chunk_id": "1", "document_title": "Doc A", "content": "Hello"}}, # Duplicate
        {"id": "2", "payload": {"chunk_id": "2", "document_title": "Doc B", "content": "World"}}
    ]
    
    context = context_assembler.assemble(chunks)
    assert "Doc A" in context
    assert "Doc B" in context
    assert context.count("Hello") == 1 # Deduplicated

def test_citation_service():
    from app.services.rag.citation_service import citation_service
    from app.services.rag.state import Citation
    
    citations = [
        Citation(chunk_id="1", claim="Valid claim"),
        Citation(chunk_id="999", claim="Hallucinated claim")
    ]
    
    retrieved_chunks = [
        {"payload": {"chunk_id": "1", "document_title": "Valid Doc"}}
    ]
    
    valid_citations = citation_service.validate_citations(citations, retrieved_chunks)
    
    assert len(valid_citations) == 1
    assert valid_citations[0].chunk_id == "1"
    assert valid_citations[0].document_title == "Valid Doc"

def test_confidence_engine():
    from app.services.rag.confidence_engine import confidence_engine
    
    # High confidence test
    score = confidence_engine.calculate_confidence(
        llm_confidence=95.0,
        retrieved_chunks=[{"score": 0.9}],
        citations_count=1
    )
    assert score > 80.0
    
    # Hallucination test (No chunks)
    score_hallucinated = confidence_engine.calculate_confidence(
        llm_confidence=99.0,
        retrieved_chunks=[],
        citations_count=0
    )
    assert score_hallucinated == 0.0

def test_escalation_service():
    from app.services.rag.escalation_service import escalation_service
    
    # Should escalate on low confidence
    assert escalation_service.evaluate(50.0, "normal query", [{"id": "1"}]) == True
    
    # Should escalate on missing chunks
    assert escalation_service.evaluate(95.0, "normal query", []) == True
    
    # Should escalate on explicit trigger
    assert escalation_service.evaluate(95.0, "I want to talk to a human", [{"id": "1"}]) == True
    
    # Should not escalate on normal
    assert escalation_service.evaluate(95.0, "how to reset password", [{"id": "1"}]) == False
