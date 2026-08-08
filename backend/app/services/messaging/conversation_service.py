import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.repositories.conversation_repo import (
    customer_repo, conversation_repo, message_repo, conversation_event_repo, customer_feedback_repo,
    CustomerInternalCreate, ConversationInternalCreate, MessageInternalCreate, ConversationEventInternalCreate,
    CustomerFeedbackInternalCreate
)
from app.models.conversation import Customer, Conversation, Message, ConversationStatus, SenderType, MessageType, CustomerFeedback

logger = logging.getLogger(__name__)

class ConversationService:
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

    async def get_workspace_conversations(
        self, 
        db: AsyncSession, 
        workspace_id: str,
        status: Optional[ConversationStatus] = None,
        assigned_user_id: Optional[str] = None
    ):
        return await conversation_repo.get_by_workspace(
            db, 
            workspace_id=workspace_id, 
            status=status, 
            assigned_user_id=assigned_user_id
        )

    async def get_conversation(self, db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        return await conversation_repo.get(db, id=conversation_id)

    async def update_status(self, db: AsyncSession, conversation_id: str, status: ConversationStatus) -> Optional[Conversation]:
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
            
        updated_conv = await conversation_repo.update(db, db_obj=conv, obj_in={"status": status})
        
        # If resolved, set resolved_at
        if status == ConversationStatus.RESOLVED:
            from datetime import datetime
            updated_conv = await conversation_repo.update(db, db_obj=updated_conv, obj_in={"resolved_at": datetime.utcnow(), "is_human_active": False})
            
        event_in = ConversationEventInternalCreate(
            conversation_id=str(conv.id),
            event_type=f"STATUS_CHANGED_TO_{status.value}"
        )
        await conversation_event_repo.create(db, obj_in=event_in)
        
        return updated_conv

    async def add_message(self, db: AsyncSession, conversation_id: str, sender_type: SenderType, content: str, sender_id: Optional[str] = None, message_type: MessageType = MessageType.TEXT) -> Message:
        msg_in = MessageInternalCreate(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            message_type=message_type
        )
        msg = await message_repo.create(db, obj_in=msg_in)
        
        await conversation_repo.update_last_message(db, conversation_id)
        return msg

    async def get_messages(self, db: AsyncSession, conversation_id: str):
        return await message_repo.get_by_conversation(db, conversation_id)
        
    async def assign_conversation(self, db: AsyncSession, conversation_id: str, assigned_user_id: str) -> Optional[Conversation]:
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
            
        updated_conv = await conversation_repo.update(db, db_obj=conv, obj_in={"assigned_user_id": assigned_user_id})
        
        event_in = ConversationEventInternalCreate(
            conversation_id=str(conv.id),
            event_type="ASSIGNED",
            metadata_={"assigned_user_id": assigned_user_id}
        )
        await conversation_event_repo.create(db, obj_in=event_in)
        return updated_conv

    async def add_feedback(self, db: AsyncSession, conversation_id: str, is_helpful: Optional[bool] = None, rating: Optional[int] = None, comment: Optional[str] = None) -> CustomerFeedback:
        fb_in = CustomerFeedbackInternalCreate(
            conversation_id=conversation_id,
            is_helpful=is_helpful,
            rating=rating,
            comment=comment
        )
        return await customer_feedback_repo.create(db, obj_in=fb_in)

class CustomerService:
    async def get_or_create_customer(self, db: AsyncSession, workspace_id: str, email: Optional[str] = None, name: Optional[str] = None) -> Customer:
        if email:
            customer = await customer_repo.get_by_email(db, workspace_id, email)
            if customer:
                # Update last seen
                return await customer_repo.update(db, db_obj=customer, obj_in={"name": name})
                
        # Anonymous or new
        cust_in = CustomerInternalCreate(
            workspace_id=workspace_id,
            name=name or "Anonymous Customer",
            email=email
        )
        return await customer_repo.create(db, obj_in=cust_in)

conversation_service = ConversationService()
customer_service = CustomerService()
