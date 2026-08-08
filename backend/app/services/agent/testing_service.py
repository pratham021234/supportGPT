from typing import Dict, Any, AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse

from app.services.rag.rag_service import rag_service
from app.services.rag.graph import build_rag_graph
from app.services.rag.state import RAGState
from app.repositories.agent_repo import agent_repo, agent_prompt_repo, agent_knowledge_scope_repo
from app.services.vector.search_service import search_service
from app.services.agent.safety_service import safety_service

class AgentTestingService:
    async def test_agent(self, db: AsyncSession, agent_id: str, query: str, user_id: str) -> Dict[str, Any]:
        """Runs the RAG pipeline but scoped specifically for this agent's knowledge and prompt."""
        
        agent = await agent_repo.get(db, id=agent_id)
        if not agent:
            raise ValueError("Agent not found")
            
        # Safety Layer: Pre-generation check
        is_safe = await safety_service.pre_generation_check(query)
        if not is_safe:
            return {
                "answer": "I'm sorry, I cannot fulfill that request.",
                "confidence_score": 0.0,
                "escalate": True
            }
            
        # 1. Fetch Agent Prompt
        prompt = await agent_prompt_repo.get_by_agent(db, agent_id)
        
        # 2. Fetch Knowledge Scope
        scopes = await agent_knowledge_scope_repo.get_by_agent(db, agent_id)
        filter_document_id = str(scopes[0].document_id) if scopes and scopes[0].document_id else None
        
        # 3. Create Scoped Retrieval Node
        async def scoped_retrieval_node(state: RAGState) -> Dict[str, Any]:
            results = await search_service.semantic_search(
                db=db,
                workspace_id=str(agent.workspace_id),
                user_id=user_id,
                query=state.query,
                limit=10,
                document_id=filter_document_id
            )
            return {"retrieved_chunks": results}
            
        # 4. Execute with custom scoped graph
        app = build_rag_graph(scoped_retrieval_node)
        
        initial_state = RAGState(
            workspace_id=str(agent.workspace_id),
            user_id=user_id,
            query=query
        )
        
        result_state = await app.ainvoke(initial_state.model_dump())
        
        # Safety Layer: Post-generation PII filter
        safe_answer = await safety_service.post_generation_filter(result_state.get("answer", ""))
        
        return {
            "answer": safe_answer,
            "confidence_score": result_state.get("confidence_score", 0.0),
            "escalate": result_state.get("escalate", False),
            "citations": result_state.get("citations", [])
        }

agent_testing_service = AgentTestingService()
