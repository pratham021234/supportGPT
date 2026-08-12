import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from sqlalchemy import select, func
from datetime import datetime

from app.models.conversation import Conversation, ConversationStatus

logger = logging.getLogger(__name__)

class ChatSessionService:
    async def get_active_sessions(self, db: AsyncSession, workspace_id: str) -> List[Conversation]:
        stmt = select(Conversation).where(
            Conversation.workspace_id == workspace_id,
            Conversation.status.in_([ConversationStatus.ACTIVE, ConversationStatus.OPEN])
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_waiting_sessions(self, db: AsyncSession, workspace_id: str) -> List[Conversation]:
        stmt = select(Conversation).where(
            Conversation.workspace_id == workspace_id,
            Conversation.status == ConversationStatus.WAITING
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_assigned_sessions(self, db: AsyncSession, workspace_id: str, user_id: str) -> List[Conversation]:
        stmt = select(Conversation).where(
            Conversation.workspace_id == workspace_id,
            Conversation.assigned_user_id == user_id,
            Conversation.status.in_([ConversationStatus.ACTIVE, ConversationStatus.OPEN, ConversationStatus.ESCALATED])
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_closed_sessions(self, db: AsyncSession, workspace_id: str) -> List[Conversation]:
        stmt = select(Conversation).where(
            Conversation.workspace_id == workspace_id,
            Conversation.status == ConversationStatus.CLOSED
        )
        result = await db.execute(stmt)
        return result.scalars().all()
        
    async def monitor_session_metrics(self, db: AsyncSession, conversation_id: str) -> Dict[str, Any]:
        conv = await db.get(Conversation, conversation_id)
        if not conv:
            return {}
            
        start_time = conv.started_at
        end_time = conv.resolved_at
        
        duration = 0
        if start_time:
            end = end_time or datetime.utcnow().replace(tzinfo=start_time.tzinfo)
            duration = (end - start_time).total_seconds()
            
        return {
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": duration,
            "status": conv.status
        }

chat_session_service = ChatSessionService()
