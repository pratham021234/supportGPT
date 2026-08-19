import pytest
import uuid
from app.services.rag.state import RAGState
from app.services.rag.nodes import query_node, retrieval_node, context_builder_node, generation_node, validation_node

@pytest.mark.asyncio
async def test_rag_query_node():
    state = RAGState(
        workspace_id=str(uuid.uuid4()),
        user_id="test_user",
        query="How do I reset my password?"
    )
    # query_node just sets language and intent (using query_processor)
    result = await query_node(state)
    
    assert "language" in result
    assert "query_type" in result
    assert "agent_routing" in result

@pytest.mark.asyncio
async def test_rag_context_builder():
    state = RAGState(
        workspace_id=str(uuid.uuid4()),
        user_id="test_user",
        query="test",
        retrieved_chunks=[
            {"id": "1", "score": 0.9, "payload": {"content": "Chunk 1", "document_title": "Doc 1"}},
            {"id": "2", "score": 0.8, "payload": {"content": "Chunk 2", "document_title": "Doc 2"}}
        ]
    )
    result = context_builder_node(state)
    assert "context_str" in result
    assert "Chunk 1" in result["context_str"]
    assert "Chunk 2" in result["context_str"]

@pytest.mark.asyncio
async def test_rag_validation_node():
    state = RAGState(
        workspace_id=str(uuid.uuid4()),
        user_id="test",
        query="test",
        answer="I don't know the answer based on context.",
        confidence_score=95.0,
        citations=[],
        retrieved_chunks=[]
    )
    
    result = validation_node(state)
    assert "confidence_score" in result
    assert "escalate" in result
    # Low confidence -> escalate
    assert result["confidence_score"] <= 50.0
