import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, cast, String
from typing import List

from app.models.conversation import Conversation, Customer, Message

logger = logging.getLogger(__name__)

class ConversationSearchService:
    async def search_conversations(self, db: AsyncSession, workspace_id: str, query: str) -> List[Conversation]:
        """
        Fast retrieval by customer, email, message content, or tags.
        """
        # A basic ilike search across related fields for MVP
        stmt = (
            select(Conversation)
            .join(Customer, Conversation.customer_id == Customer.id)
            .outerjoin(Message, Conversation.id == Message.conversation_id)
            .where(
                Conversation.workspace_id == workspace_id,
                or_(
                    Customer.name.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                    Message.content.ilike(f"%{query}%"),
                    cast(Conversation.metadata_, String).ilike(f"%{query}%")
                )
            )
            .distinct()
        )
        
        result = await db.execute(stmt)
        return result.scalars().all()

conversation_search_service = ConversationSearchService()
