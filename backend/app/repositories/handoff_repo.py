from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.repositories.base import BaseRepository
from app.models.handoff import (
    AgentPresence, AgentQueue, ConversationHandoff, AgentPresenceStatus, QueueAssignment
)
from pydantic import BaseModel

class AgentPresenceInternalCreate(BaseModel):
    workspace_id: str
    user_id: str
    current_status: AgentPresenceStatus = AgentPresenceStatus.OFFLINE
    active_conversations: int = 0

class AgentQueueInternalCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    priority: int = 1

class ConversationHandoffInternalCreate(BaseModel):
    conversation_id: str
    from_agent_id: Optional[str] = None
    to_user_id: Optional[str] = None
    reason: Optional[str] = None
    initiated_by: str

class AgentPresenceRepository(BaseRepository[AgentPresence, AgentPresenceInternalCreate, BaseModel]):
    async def get_by_user(self, db: AsyncSession, workspace_id: str, user_id: str) -> Optional[AgentPresence]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id,
            self.model.user_id == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_workspace_presence(self, db: AsyncSession, workspace_id: str) -> List[AgentPresence]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id
        ).order_by(desc(self.model.last_seen))
        result = await db.execute(query)
        return list(result.scalars().all())

class AgentQueueRepository(BaseRepository[AgentQueue, AgentQueueInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[AgentQueue]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id
        ).order_by(desc(self.model.priority))
        result = await db.execute(query)
        return list(result.scalars().all())

class ConversationHandoffRepository(BaseRepository[ConversationHandoff, ConversationHandoffInternalCreate, BaseModel]):
    pass

presence_repo = AgentPresenceRepository(AgentPresence)
queue_repo = AgentQueueRepository(AgentQueue)
handoff_repo = ConversationHandoffRepository(ConversationHandoff)
