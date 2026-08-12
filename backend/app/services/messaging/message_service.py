import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.models.conversation import Message, SenderType, MessageType
from app.repositories.conversation_repo import message_repo, MessageInternalCreate, conversation_repo

logger = logging.getLogger(__name__)

class MessageService:
    async def store_message(
        self, 
        db: AsyncSession, 
        conversation_id: str, 
        sender_type: SenderType, 
        content: str, 
        sender_id: Optional[str] = None, 
        message_type: MessageType = MessageType.TEXT, 
        metadata_: Optional[Dict[str, Any]] = None,
        sources: Optional[list] = None,
        confidence: Optional[float] = None
    ) -> Message:
        
        meta = metadata_ or {}
        if sources is not None:
            meta["sources"] = sources
        if confidence is not None:
            meta["confidence"] = confidence

        msg_in = MessageInternalCreate(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            metadata_=meta
        )
        msg = await message_repo.create(db, obj_in=msg_in)
        
        # Update conversation last_message_at
        await conversation_repo.update_last_message(db, conversation_id)
        
        return msg

    async def get_messages(self, db: AsyncSession, conversation_id: str):
        return await message_repo.get_by_conversation(db, conversation_id)

message_service = MessageService()
