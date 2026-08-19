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
from app.services.llm.orchestrator import llm_orchestrator
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
    from app.services.rag.retrieval_engine import retrieval_engine
    from app.core.database import async_session_maker
    
    logger.info(f"Retrieval Node searching for workspace: {state.workspace_id}")
    
    async with async_session_maker() as db:
        top_chunks = await retrieval_engine.retrieve(
            db=db,
            workspace_id=state.workspace_id,
            user_id=state.user_id,
            query=state.query,
            keywords=state.keywords,
            limit=5, # Top 5
            agent_routing=state.agent_routing
        )
        
    return {"retrieved_chunks": top_chunks}

def context_builder_node(state: RAGState) -> Dict[str, Any]:
    """Formats retrieved chunks into a single context string while preserving metadata."""
    logger.info(f"Context Node building from {len(state.retrieved_chunks)} chunks")
    
    context_str = context_assembler.assemble(state.retrieved_chunks)
    return {"context_str": context_str}

async def generation_node(state: RAGState) -> Dict[str, Any]:
    """Generates the answer with citations using LLM Provider."""
    logger.info("Generation Node running...")
    
    # 1. Build Prompt dynamically
    prompt = await prompt_builder.build_prompt(
        context=state.context_str,
        query=state.query,
        agent_routing=state.agent_routing,
        workspace_id=state.workspace_id
    )
    
    # Check if streaming callback exists in metadata
    streaming_callback = state.metadata.get("streaming_callback") if state.metadata else None
    
    if streaming_callback:
        # Use streaming capability
        logger.info("Generation Node using streaming...")
        final_answer = ""
        citations = []
        confidence_score = 0.0
        
        async for chunk in llm_orchestrator.astream_structured_answer(
            prompt=prompt,
            context=state.context_str,
            query=state.query
        ):
            if isinstance(chunk, dict):
                # End of stream parsed result or partial dict
                final_answer = chunk.get("answer", final_answer)
                citations = chunk.get("citations", citations)
                confidence_score = chunk.get("confidence_score", confidence_score)
                # Pass partial event to callback
                await streaming_callback({"event": "generation_chunk", "data": chunk})
            else:
                # Assuming chunk is text or generic stream item
                await streaming_callback({"event": "generation_chunk", "data": {"text": str(chunk)}})
        
        return {
            "answer": final_answer,
            "citations": citations,
            "confidence_score": confidence_score
        }
    
    # 2. Generate structured answer via Provider
    result = await llm_orchestrator.generate_structured_answer(
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
