import pytest
from app.services.rag.state import RAGState, Citation
from app.services.rag.nodes import context_builder_node, validation_node

def test_context_builder_node_empty():
    state = RAGState(workspace_id="123", query="test")
    state.retrieved_chunks = []
    
    result = context_builder_node(state)
    assert result["context_str"] == "No relevant documents found."

def test_context_builder_node_with_chunks():
    state = RAGState(workspace_id="123", query="test")
    state.retrieved_chunks = [
        {"id": "chunk-1", "payload": {"chunk_id": "chunk-1", "document_title": "Doc 1", "content": "Content 1"}},
        {"id": "chunk-2", "payload": {"document_title": "Doc 2", "content": "Content 2"}} # Fallback to hit.id if chunk_id missing
    ]
    
    result = context_builder_node(state)
    assert "SOURCE ID: chunk-1" in result["context_str"]
    assert "DOCUMENT: Doc 1" in result["context_str"]
    assert "CONTENT:\nContent 1" in result["context_str"]
    assert "SOURCE ID: chunk-2" in result["context_str"]

def test_validation_node_high_confidence():
    state = RAGState(workspace_id="123", query="test", confidence_score=95.0)
    state.retrieved_chunks = [{"id": "chunk-1"}]
    
    result = validation_node(state)
    assert result["escalate"] is False

def test_validation_node_low_confidence():
    state = RAGState(workspace_id="123", query="test", confidence_score=60.0)
    state.retrieved_chunks = [{"id": "chunk-1"}]
    
    result = validation_node(state)
    assert result["escalate"] is True

def test_validation_node_hallucination_prevention():
    # Model gave high confidence, but there was NO context.
    state = RAGState(workspace_id="123", query="test", confidence_score=95.0)
    state.retrieved_chunks = []
    
    result = validation_node(state)
    assert result["confidence_score"] == 0.0
    assert result["escalate"] is True
