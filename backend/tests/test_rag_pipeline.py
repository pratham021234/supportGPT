import pytest
from typing import Dict, Any, AsyncGenerator

from app.services.rag.state import RAGState, Citation
from app.services.rag.query_expansion import query_expansion_service
from app.services.rag.agent_router import agent_router
from app.services.rag.context_ranking import context_ranking_service
from app.services.rag.hallucination_guard import hallucination_guard
from app.services.llm.gemini_provider import GeminiProvider

def test_query_expansion():
    keywords = ["password", "issue"]
    expanded = query_expansion_service.expand_query("how to reset password", keywords)
    assert "password" in expanded
    assert "credentials" in expanded or "login" in expanded

def test_agent_router():
    assert agent_router.determine_agent("SALES", "") == "SALES"
    assert agent_router.determine_agent("TROUBLESHOOTING", "") == "TECHNICAL"
    assert agent_router.determine_agent("UNKNOWN", "") == "SUPPORT"

def test_context_ranking():
    chunks = [
        {"id": "1", "score": 0.8, "payload": {"source_type": "FAQ", "agent_id": "GLOBAL"}},
        {"id": "2", "score": 0.9, "payload": {"source_type": "UNKNOWN", "agent_id": "SALES"}}
    ]
    ranked = context_ranking_service.rank_context(chunks, "SALES")
    assert len(ranked) == 2
    # Ensure they have ranked_score
    assert "ranked_score" in ranked[0]

def test_hallucination_guard():
    # True means it's a hallucination
    # No context = hallucination
    assert hallucination_guard.check_hallucinations("Answer", 0, []) == True
    # Has context, has citations = safe
    assert hallucination_guard.check_hallucinations("Answer", 1, [{"id": "1"}]) == False
    # No citations, but has context and is a valid fallback = safe
    assert hallucination_guard.check_hallucinations("I could not find", 0, [{"id": "1"}]) == False

@pytest.mark.asyncio
async def test_gemini_provider():
    # Testing graceful degradation without API key
    provider = GeminiProvider()
    res = await provider.generate_structured_answer("prompt", "context", "query")
    assert "answer" in res
    assert "confidence_score" in res
