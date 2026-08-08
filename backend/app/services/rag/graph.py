from langgraph.graph import StateGraph, END
from typing import Callable, Any

from app.services.rag.state import RAGState
from app.services.rag.nodes import (
    query_node,
    context_builder_node,
    generation_node,
    validation_node
)

def build_rag_graph(retrieval_node: Callable[[RAGState], Any]):
    """
    Builds the LangGraph state machine for RAG.
    We pass in the retrieval_node dynamically so it can access the DB session.
    """
    workflow = StateGraph(RAGState)

    # Add Nodes
    workflow.add_node("query_understanding", query_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("validation", validation_node)

    # Add Edges (Linear Flow)
    workflow.set_entry_point("query_understanding")
    workflow.add_edge("query_understanding", "retrieval")
    workflow.add_edge("retrieval", "context_builder")
    workflow.add_edge("context_builder", "generation")
    workflow.add_edge("generation", "validation")
    workflow.add_edge("validation", END)

    # Compile
    return workflow.compile()
