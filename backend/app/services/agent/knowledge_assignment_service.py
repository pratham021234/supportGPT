import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.models.agent import AgentKnowledgeScope
from app.repositories.agent_repo import agent_knowledge_scope_repo, AgentKnowledgeScopeInternalCreate

logger = logging.getLogger(__name__)

class KnowledgeAssignmentService:
    async def assign_document(self, db: AsyncSession, agent_id: str, document_id: str) -> AgentKnowledgeScope:
        scope_in = AgentKnowledgeScopeInternalCreate(
            agent_id=agent_id,
            document_id=document_id
        )
        return await agent_knowledge_scope_repo.create(db, obj_in=scope_in)
        
    async def assign_source(self, db: AsyncSession, agent_id: str, source_id: str) -> AgentKnowledgeScope:
        scope_in = AgentKnowledgeScopeInternalCreate(
            agent_id=agent_id,
            source_id=source_id
        )
        return await agent_knowledge_scope_repo.create(db, obj_in=scope_in)

    async def get_agent_knowledge(self, db: AsyncSession, agent_id: str) -> List[AgentKnowledgeScope]:
        return await agent_knowledge_scope_repo.get_by_agent(db, agent_id)
        
    async def remove_assignment(self, db: AsyncSession, scope_id: str):
        await agent_knowledge_scope_repo.remove(db, id=scope_id)

knowledge_assignment_service = KnowledgeAssignmentService()
