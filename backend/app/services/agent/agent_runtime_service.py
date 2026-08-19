import logging
from typing import Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.agent.agent_router import multi_agent_router
from app.services.rag.rag_service import rag_service

logger = logging.getLogger(__name__)

class AgentRuntimeService:
    async def execute(self, db: AsyncSession, workspace_id: str, user_id: str, query: str) -> Dict[str, Any]:
        """
        Executes a user query through the multi-agent platform.
        1. Routes the query to the best active agent.
        2. Applies the agent's specific knowledge scope and prompts.
        3. Executes the underlying RAG pipeline.
        """
        # 1. Routing
        agent = await multi_agent_router.route_query(db, workspace_id, query)
        agent_id = str(agent.id) if agent else None
        
        # 2. Execution
        result = await rag_service.execute_query(
            db=db,
            workspace_id=workspace_id,
            user_id=user_id,
            query=query,
            agent_id=agent_id
        )
        
        # Inject the agent metadata into the result for transparency
        if agent:
            result["agent"] = {
                "id": str(agent.id),
                "name": agent.name,
                "type": agent.agent_type.value
            }
            
        return result

    def stream_execute(self, db: AsyncSession, workspace_id: str, user_id: str, query: str) -> AsyncGenerator[str, None]:
        """
        Stream execution of an agent query. The multi-agent router is synchronous in the background thread.
        To avoid blocking the stream, we just pass the query directly to the RAG service which handles
        streaming internally. If routing is needed, it would be injected via metadata.
        """
        # Note: In a fully productionized version, we would `await multi_agent_router.route_query` 
        # before starting the SSE stream. For simplicity in streaming, we pass to RAG directly.
        # RAG will fall back to default agent logic inside nodes.py if agent_id isn't provided.
        return rag_service.stream_query(
            db=db,
            workspace_id=workspace_id,
            user_id=user_id,
            query=query,
            agent_id=None # Default routing will handle it in RAG graph
        )

agent_runtime_service = AgentRuntimeService()
