import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.repositories.handoff_repo import (
    presence_repo, queue_repo, handoff_repo,
    AgentPresenceInternalCreate, AgentQueueInternalCreate, ConversationHandoffInternalCreate,
    AgentPresenceStatus, AgentPresence, AgentQueue, ConversationHandoff
)
from app.repositories.conversation_repo import conversation_repo

logger = logging.getLogger(__name__)

class PresenceService:
    async def get_presence(self, db: AsyncSession, workspace_id: str, user_id: str) -> AgentPresence:
        presence = await presence_repo.get_by_user(db, workspace_id, user_id)
        if not presence:
            presence_in = AgentPresenceInternalCreate(
                workspace_id=workspace_id,
                user_id=user_id,
                current_status=AgentPresenceStatus.ONLINE,
                active_conversations=0
            )
            presence = await presence_repo.create(db, obj_in=presence_in)
        return presence

    async def update_status(self, db: AsyncSession, workspace_id: str, user_id: str, status: AgentPresenceStatus) -> AgentPresence:
        presence = await self.get_presence(db, workspace_id, user_id)
        return await presence_repo.update(db, db_obj=presence, obj_in={"current_status": status})
        
    async def get_workspace_presence(self, db: AsyncSession, workspace_id: str):
        return await presence_repo.get_workspace_presence(db, workspace_id)

class QueueService:
    async def create_queue(self, db: AsyncSession, workspace_id: str, name: str, description: Optional[str] = None, priority: int = 1) -> AgentQueue:
        queue_in = AgentQueueInternalCreate(
            workspace_id=workspace_id,
            name=name,
            description=description,
            priority=priority
        )
        return await queue_repo.create(db, obj_in=queue_in)
        
    async def get_queues(self, db: AsyncSession, workspace_id: str):
        return await queue_repo.get_by_workspace(db, workspace_id)


class HandoffService:
    async def initiate_handoff(self, db: AsyncSession, conversation_id: str, from_agent_id: Optional[str], to_user_id: Optional[str], reason: str, initiated_by: str) -> ConversationHandoff:
        """Called when AI explicitly fails, or customer requests human."""
        
        handoff_in = ConversationHandoffInternalCreate(
            conversation_id=conversation_id,
            from_agent_id=from_agent_id,
            to_user_id=to_user_id,
            reason=reason,
            initiated_by=initiated_by
        )
        handoff = await handoff_repo.create(db, obj_in=handoff_in)
        
        # Mark conversation as waiting for human
        # But we don't activate the human flag until they accept
        
        return handoff

    async def accept_handoff(self, db: AsyncSession, conversation_id: str, user_id: str) -> bool:
        """Called when a human agent accepts the conversation from the queue."""
        
        # 1. Fetch conversation
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return False
            
        # 2. Mark human active (this pauses RAG execution in the websocket handler)
        await conversation_repo.update(db, db_obj=conv, obj_in={"is_human_active": True})
        
        # 3. Increment active conversations for agent presence
        presence = await presence_repo.get_by_user(db, str(conv.workspace_id), user_id)
        if presence:
            await presence_repo.update(db, db_obj=presence, obj_in={"active_conversations": presence.active_conversations + 1})
            
        return True
        
    async def release_handoff(self, db: AsyncSession, conversation_id: str, user_id: str) -> bool:
        """Human leaves, optionally gives back to AI."""
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return False
            
        await conversation_repo.update(db, db_obj=conv, obj_in={"is_human_active": False})
        
        presence = await presence_repo.get_by_user(db, str(conv.workspace_id), user_id)
        if presence and presence.active_conversations > 0:
            await presence_repo.update(db, db_obj=presence, obj_in={"active_conversations": presence.active_conversations - 1})
            
        return True

class AIAssistService:
    async def generate_summary(self, db: AsyncSession, conversation_id: str) -> str:
        """
        Uses Gemini (or another LLM) to summarize the conversation history for the live agent.
        Since we are just structuring, we'll return a mock string for MVP.
        """
        return "Customer is experiencing issues with API rate limiting. AI recommended upgrading tier, but customer requested human."

presence_service = PresenceService()
queue_service = QueueService()
handoff_service = HandoffService()
ai_assist_service = AIAssistService()
