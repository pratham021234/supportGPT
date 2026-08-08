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
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Initialize LLM. 
# We use Gemini 2.5 Flash as requested.
# If no key is set, we will gracefully degrade in the node itself.
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=settings.GEMINI_API_KEY
    )
    # We will use structured outputs for generation
    structured_llm = llm.with_structured_output(AnswerOutput)
except Exception:
    llm = None
    structured_llm = None

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
    """Generates the answer with citations using Gemini structured outputs."""
    logger.info("Generation Node running...")
    
    if not structured_llm:
        # Fallback if no API key
        return {
            "answer": "Gemini API Key is missing. I cannot generate an answer.",
            "citations": [],
            "confidence_score": 0.0
        }
        
    prompt = PromptTemplate.from_template("""
You are SupportGPT, a professional, helpful, and highly accurate enterprise AI support agent.
You must answer the user's question using ONLY the provided knowledge base context.

CRITICAL RULES:
1. NEVER fabricate information, policies, or procedures.
2. If the context does not contain the answer, say "I could not find reliable information in the available knowledge base."
3. Always cite your sources using the SOURCE ID provided in the context.
4. Be concise but complete.
5. Provide a confidence_score (0.0 to 100.0) based on how well the context answers the query. If you are unsure, provide a low score.

CONTEXT:
{context}

USER QUESTION:
{query}
""")
    
    try:
        chain = prompt | structured_llm
        result: AnswerOutput = await chain.ainvoke({
            "context": state.context_str,
            "query": state.query
        })
        
        return {
            "answer": result.answer,
            "citations": result.citations,
            "confidence_score": result.confidence_score
        }
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return {
            "answer": "An error occurred during generation.",
            "citations": [],
            "confidence_score": 0.0
        }

def validation_node(state: RAGState) -> Dict[str, Any]:
    """Validates the answer, adjusts confidence, and evaluates escalation."""
    logger.info("Validation Node checking answer.")
    
    # Validate citations
    valid_citations = citation_service.validate_citations(
        state.citations, 
        state.retrieved_chunks
    )
    
    # Calculate confidence
    final_confidence = confidence_engine.calculate_confidence(
        llm_confidence=state.confidence_score,
        retrieved_chunks=state.retrieved_chunks,
        citations_count=len(valid_citations)
    )
    
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
