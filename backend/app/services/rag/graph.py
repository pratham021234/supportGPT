from langgraph.graph import StateGraph, END
from typing import Callable, Any

from app.services.rag.state import RAGState
from app.services.rag.nodes import (
    query_node,
    context_builder_node,
    generation_node,
    validation_node
)
from app.services.agent.agent_router import multi_agent_router
from app.dependencies.db import async_session_maker

# New Node for multi-agent dynamic selection
async def agent_selection_node(state: RAGState) -> dict:
    """
    Evaluates the intent of the query and assigns an agent if not already assigned.
    """
    if state.metadata and state.metadata.get("agent_id"):
        return {} # Agent already selected
        
    async with async_session_maker() as db:
        agent = await multi_agent_router.route_query(db, state.workspace_id, state.query)
        if agent:
            metadata = state.metadata or {}
            metadata["agent_id"] = str(agent.id)
            return {"metadata": metadata}
    return {}

def build_rag_graph(retrieval_node: Callable[[RAGState], Any]):
    """
    Builds the LangGraph state machine for SupportGPT Multi-Agent ecosystem.
    """
    workflow = StateGraph(RAGState)

    # Add Nodes
    workflow.add_node("agent_selection", agent_selection_node)
    workflow.add_node("query_understanding", query_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("validation", validation_node)

    # Add Edges (Linear Flow with explicit routing node first)
    workflow.set_entry_point("agent_selection")
    workflow.add_edge("agent_selection", "query_understanding")
    workflow.add_edge("query_understanding", "retrieval")
    workflow.add_edge("retrieval", "context_builder")
    workflow.add_edge("context_builder", "generation")
    workflow.add_edge("generation", "validation")
    workflow.add_edge("validation", END)

    # Compile
    return workflow.compile()
