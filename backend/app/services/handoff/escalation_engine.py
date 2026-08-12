import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.conversation import Conversation
from app.services.handoff.human_handoff_service import human_handoff_service
from app.services.ticketing.ticket_creation_service import ticket_creation_service
from app.services.notifications.notification_service import notification_service

logger = logging.getLogger(__name__)

class EscalationEngine:
    async def evaluate_escalation(self, db: AsyncSession, conversation: Conversation, confidence_score: Optional[float] = None, is_negative_feedback: bool = False, is_vip: bool = False) -> bool:
        """
        Evaluates rules for automatic escalation.
        Returns True if escalated, False otherwise.
        """
        reason = None
        
        if confidence_score is not None and confidence_score < 70.0:
            reason = f"Low AI Confidence ({confidence_score} < 70.0)"
            
        elif is_negative_feedback:
            reason = "Negative Customer Feedback"
            
        elif is_vip:
            reason = "VIP Customer Automatic Routing"
            
        # For SLA risk, we might check time since start
        from datetime import datetime
        if not reason and conversation.started_at:
            elapsed_minutes = (datetime.utcnow().replace(tzinfo=None) - conversation.started_at.replace(tzinfo=None)).total_seconds() / 60
            if elapsed_minutes > 15: # 15 minutes unresolved by AI
                reason = "SLA Risk (15m unresolved)"
                
        if reason:
            logger.info(f"Escalation triggered for conv {conversation.id}: {reason}")
            
            # Trigger handoff
            await human_handoff_service.trigger_handoff(
                db=db,
                conversation_id=str(conversation.id),
                reason=reason,
                initiated_by="SYSTEM",
                from_agent_id=str(conversation.agent_id) if conversation.agent_id else None
            )
            
            # Create a ticket for the escalation
            ticket = await ticket_creation_service.create_ai_escalation(
                db=db,
                workspace_id=str(conversation.workspace_id),
                conversation_id=str(conversation.id),
                customer_id=str(conversation.customer_id),
                reason=reason
            )
            
            # Notify admins or queue watchers (broadly notify on workspace)
            await notification_service.notify_escalation(str(conversation.workspace_id), str(conversation.id), reason)
            return True
            
        return False

escalation_engine = EscalationEngine()
