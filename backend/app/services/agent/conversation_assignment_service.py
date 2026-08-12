import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.conversation import Conversation
from app.services.agent.agent_presence_service import agent_presence_service
from app.services.messaging.conversation_engine import conversation_engine
from app.services.notifications.notification_service import notification_service

logger = logging.getLogger(__name__)

class ConversationAssignmentService:
    async def assign_least_busy_agent(self, db: AsyncSession, conversation: Conversation) -> Optional[str]:
        """Finds the least busy available agent and assigns the conversation."""
        workspace_id = str(conversation.workspace_id)
        
        available_agents = await agent_presence_service.get_available_agents(db, workspace_id)
        if not available_agents:
            logger.info("No available agents for assignment.")
            return None
            
        # Load balancing: sort by active conversations ascending
        available_agents.sort(key=lambda a: a.active_conversations)
        best_agent = available_agents[0]
        assigned_user_id = str(best_agent.user_id)
        
        # Assign conversation
        await conversation_engine.transfer_conversation(db, str(conversation.id), assigned_user_id)
        
        # Update presence
        await agent_presence_service.increment_active_conversations(db, workspace_id, assigned_user_id)
        
        # Notify agent
        await notification_service.notify_agent_assigned(assigned_user_id, str(conversation.id))
        
        logger.info(f"Assigned conversation {conversation.id} to user {assigned_user_id}")
        return assigned_user_id

conversation_assignment_service = ConversationAssignmentService()
