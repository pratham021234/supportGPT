from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.conversation import (
    Customer, Conversation, Message, ConversationAssignment, ConversationEvent,
    ConversationStatus, ConversationChannel, SenderType, MessageType, CustomerFeedback
)
from pydantic import BaseModel

class CustomerInternalCreate(BaseModel):
    workspace_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    external_id: Optional[str] = None

class ConversationInternalCreate(BaseModel):
    workspace_id: str
    customer_id: str
    agent_id: Optional[str] = None
    status: ConversationStatus = ConversationStatus.OPEN
    channel: ConversationChannel = ConversationChannel.WEB_CHAT

class MessageInternalCreate(BaseModel):
    conversation_id: str
    sender_type: SenderType
    sender_id: Optional[str] = None
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata_: Optional[Dict[str, Any]] = None

class ConversationEventInternalCreate(BaseModel):
    conversation_id: str
    event_type: str
    metadata_: Optional[Dict[str, Any]] = None

class CustomerFeedbackInternalCreate(BaseModel):
    conversation_id: str
    is_helpful: Optional[bool] = None
    rating: Optional[int] = None
    comment: Optional[str] = None

class CustomerRepository(BaseRepository[Customer, CustomerInternalCreate, BaseModel]):
    async def get_by_email(self, db: AsyncSession, workspace_id: str, email: str) -> Optional[Customer]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id,
            self.model.email == email
        )
        result = await db.execute(query)
        return result.scalars().first()

class ConversationRepository(BaseRepository[Conversation, ConversationInternalCreate, BaseModel]):
    async def get_by_workspace(
        self, 
        db: AsyncSession, 
        workspace_id: str,
        status: Optional[ConversationStatus] = None,
        assigned_user_id: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Conversation]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        
        if status:
            query = query.where(self.model.status == status)
        if assigned_user_id:
            query = query.where(self.model.assigned_user_id == assigned_user_id)
            
        query = query.order_by(desc(self.model.last_message_at))
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_last_message(self, db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        conv = await self.get(db, id=conversation_id)
        if conv:
            conv.last_message_at = datetime.utcnow()
            await db.commit()
            await db.refresh(conv)
        return conv

class MessageRepository(BaseRepository[Message, MessageInternalCreate, BaseModel]):
    async def get_by_conversation(self, db: AsyncSession, conversation_id: str) -> List[Message]:
        query = select(self.model).where(
            self.model.conversation_id == conversation_id
        ).order_by(self.model.created_at)
        result = await db.execute(query)
        return list(result.scalars().all())

class ConversationEventRepository(BaseRepository[ConversationEvent, ConversationEventInternalCreate, BaseModel]):
    pass

class CustomerFeedbackRepository(BaseRepository[CustomerFeedback, CustomerFeedbackInternalCreate, BaseModel]):
    async def get_by_conversation(self, db: AsyncSession, conversation_id: str) -> Optional[CustomerFeedback]:
        query = select(self.model).where(self.model.conversation_id == conversation_id)
        result = await db.execute(query)
        return result.scalars().first()

customer_repo = CustomerRepository(Customer)
conversation_repo = ConversationRepository(Conversation)
message_repo = MessageRepository(Message)
conversation_event_repo = ConversationEventRepository(ConversationEvent)
customer_feedback_repo = CustomerFeedbackRepository(CustomerFeedback)
