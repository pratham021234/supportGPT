import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conversation_repo import message_repo
from app.models.conversation import Message

logger = logging.getLogger(__name__)

class AgentMemoryService:
    async def get_conversation_context(self, db: AsyncSession, conversation_id: str, limit: int = 10) -> str:
        """
        Retrieves the last N messages of a conversation and formats them as a string transcript 
        for injection into the LangGraph state.
        """
        messages = await message_repo.get_by_conversation(db, conversation_id)
        # Assuming messages are returned oldest to newest, grab the last `limit`
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        transcript = []
        for msg in recent_messages:
            sender = msg.sender_type.value
            content = msg.content
            transcript.append(f"{sender}: {content}")
            
        return "\n".join(transcript)

agent_memory_service = AgentMemoryService()
