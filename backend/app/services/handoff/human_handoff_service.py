import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.conversation import ConversationStatus
from app.services.messaging.conversation_engine import conversation_engine
from app.services.agent.conversation_assignment_service import conversation_assignment_service
from app.repositories.handoff_repo import ConversationHandoffInternalCreate, handoff_repo
from app.repositories.conversation_repo import conversation_repo

logger = logging.getLogger(__name__)

class HumanHandoffService:
    async def trigger_handoff(
        self, 
        db: AsyncSession, 
        conversation_id: str, 
        reason: str, 
        initiated_by: str, 
        from_agent_id: Optional[str] = None
    ):
        """Called when a handoff to human is explicitly requested or escalated."""
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return None
            
        # 1. Update status to WAITING
        await conversation_engine.update_conversation(db, conversation_id, {"status": ConversationStatus.WAITING})
        
        # 2. Record Handoff intent
        handoff_in = ConversationHandoffInternalCreate(
            conversation_id=conversation_id,
            from_agent_id=from_agent_id,
            to_user_id=None,
            reason=reason,
            initiated_by=initiated_by
        )
        handoff = await handoff_repo.create(db, obj_in=handoff_in)
        
        # 3. Attempt Auto Assignment
        assigned_user = await conversation_assignment_service.assign_least_busy_agent(db, conv)
        if assigned_user:
            # Update handoff record with assigned user
            await handoff_repo.update(db, db_obj=handoff, obj_in={"to_user_id": assigned_user})
            # Transition to ACTIVE now that human is assigned (or keep it waiting until they accept? Let's assume auto-assignment means they got it)
            await conversation_engine.update_conversation(db, conversation_id, {"status": ConversationStatus.ACTIVE, "is_human_active": True})
            
        return handoff

human_handoff_service = HumanHandoffService()
