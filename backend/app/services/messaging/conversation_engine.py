import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
from datetime import datetime

from app.models.conversation import Conversation, ConversationStatus
from app.repositories.conversation_repo import conversation_repo, conversation_event_repo, ConversationInternalCreate, ConversationEventInternalCreate

logger = logging.getLogger(__name__)

class ConversationEngine:
    async def create_conversation(self, db: AsyncSession, workspace_id: str, customer_id: str, agent_id: Optional[str] = None) -> Conversation:
        conv_in = ConversationInternalCreate(
            workspace_id=workspace_id,
            customer_id=customer_id,
            agent_id=agent_id
        )
        conv = await conversation_repo.create(db, obj_in=conv_in)
        
        event_in = ConversationEventInternalCreate(
            conversation_id=str(conv.id),
            event_type="CREATED"
        )
        await conversation_event_repo.create(db, obj_in=event_in)
        return conv

    async def update_conversation(self, db: AsyncSession, conversation_id: str, update_data: dict) -> Optional[Conversation]:
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
        return await conversation_repo.update(db, db_obj=conv, obj_in=update_data)

    async def archive_conversation(self, db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
        current_metadata = conv.metadata_ or {}
        current_metadata["archived"] = True
        return await conversation_repo.update(db, db_obj=conv, obj_in={"metadata_": current_metadata, "status": ConversationStatus.CLOSED})

    async def close_conversation(self, db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
            
        updated_conv = await conversation_repo.update(db, db_obj=conv, obj_in={"status": ConversationStatus.CLOSED, "resolved_at": datetime.utcnow()})
        
        event_in = ConversationEventInternalCreate(
            conversation_id=str(conv.id),
            event_type="CLOSED"
        )
        await conversation_event_repo.create(db, obj_in=event_in)
        return updated_conv

    async def transfer_conversation(self, db: AsyncSession, conversation_id: str, assigned_user_id: str) -> Optional[Conversation]:
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
            
        updated_conv = await conversation_repo.update(db, db_obj=conv, obj_in={"assigned_user_id": assigned_user_id})
        
        event_in = ConversationEventInternalCreate(
            conversation_id=str(conv.id),
            event_type="TRANSFERRED",
            metadata_={"assigned_user_id": assigned_user_id}
        )
        await conversation_event_repo.create(db, obj_in=event_in)
        return updated_conv

conversation_engine = ConversationEngine()
