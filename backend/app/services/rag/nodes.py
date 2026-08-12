import logging
from typing import Dict, Any
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import asyncio

from app.services.rag.state import RAGState, AnswerOutput
from app.services.rag.query_processor import query_processor
from app.services.rag.context_assembler import context_assembler
from app.services.rag.citation_service import citation_service
from app.services.rag.confidence_engine import confidence_engine
from app.services.rag.escalation_service import escalation_service
from app.services.llm.gemini_provider import gemini_provider
from app.services.rag.prompt_builder import prompt_builder
from app.services.rag.hallucination_guard import hallucination_guard
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def query_node(state: RAGState) -> Dict[str, Any]:
    """Analyzes the query (Language, Type, Keywords, Routing)"""
    logger.info(f"Query Node processing: {state.query}")
    result = await query_processor.process_query(state.query)
    
    return {
        "language": result.get("language", "en"),
        "query_type": result.get("intent", "GENERAL"),
        "keywords": result.get("keywords", []),
        "agent_routing": result.get("agent_routing", "SUPPORT")
    }

async def retrieval_node(state: RAGState) -> Dict[str, Any]:
    """Retrieves relevant chunks from Qdrant via Module 7 search_service"""
    logger.info(f"Retrieval Node searching for workspace: {state.workspace_id}")
    
    # We don't have the db session here natively in LangGraph unless passed via config.
    # But search_service is async and requires db if it logs events.
    # Wait, search_service in Module 7 requires `db`. We'll pass it in the config or skip event logging in the graph node.
    # For now, we can create a temporary session if needed, or we modify the graph caller to pass db.
    pass
    # We will implement this inside the graph.py where we have access to the DB context.
    return {}

def context_builder_node(state: RAGState) -> Dict[str, Any]:
    """Formats retrieved chunks into a single context string while preserving metadata."""
    logger.info(f"Context Node building from {len(state.retrieved_chunks)} chunks")
    
    context_str = context_assembler.assemble(state.retrieved_chunks)
    return {"context_str": context_str}

async def generation_node(state: RAGState) -> Dict[str, Any]:
    """Generates the answer with citations using LLM Provider."""
    logger.info("Generation Node running...")
    
    # 1. Build Prompt dynamically
    prompt = prompt_builder.build_prompt(
        context=state.context_str,
        query=state.query,
        agent_type=state.agent_routing,
        workspace_id=state.workspace_id
    )
    
    # 2. Generate structured answer via Provider
    result = await gemini_provider.generate_structured_answer(
        prompt=prompt,
        context=state.context_str,
        query=state.query
    )
    
    return {
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "confidence_score": result.get("confidence_score", 0.0)
    }

def validation_node(state: RAGState) -> Dict[str, Any]:
    """Validates the answer, adjusts confidence, and evaluates escalation."""
    logger.info("Validation Node checking answer.")
    
    # Validate citations
    valid_citations = citation_service.validate_citations(
        state.citations, 
        state.retrieved_chunks
    )
    
    # Hallucination Guard
    is_hallucination = hallucination_guard.check_hallucinations(
        answer=state.answer,
        citations_count=len(valid_citations),
        retrieved_chunks=state.retrieved_chunks
    )
    
    # Calculate confidence
    final_confidence = confidence_engine.calculate_confidence(
        llm_confidence=state.confidence_score,
        retrieved_chunks=state.retrieved_chunks,
        citations_count=len(valid_citations)
    )
    
    if is_hallucination:
        final_confidence = min(final_confidence, 40.0) # Force low confidence to trigger escalation
    
    # Evaluate Escalation
    escalate = escalation_service.evaluate(
        confidence_score=final_confidence,
        query=state.query,
        retrieved_chunks=state.retrieved_chunks
    )
    
    return {
        "citations": valid_citations,
        "confidence_score": final_confidence,
        "escalate": escalate
    }
