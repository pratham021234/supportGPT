import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.repositories.ticket_repo import ticket_repo, ticket_activity_repo, TicketActivityInternalCreate

logger = logging.getLogger(__name__)

class TicketEscalationService:
    async def escalate_ticket(self, db: AsyncSession, ticket_id: str, reason: str, actor_id: Optional[str] = None) -> Optional[Ticket]:
        ticket = await ticket_repo.get(db, id=ticket_id)
        if not ticket:
            return None
            
        # If it's not already URGENT or CRITICAL, bump priority
        new_priority = ticket.priority
        if ticket.priority == TicketPriority.LOW:
            new_priority = TicketPriority.MEDIUM
        elif ticket.priority == TicketPriority.MEDIUM:
            new_priority = TicketPriority.HIGH
        elif ticket.priority == TicketPriority.HIGH:
            new_priority = TicketPriority.URGENT
            
        update_data = {
            "status": TicketStatus.ESCALATED,
            "priority": new_priority
        }
        
        updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in=update_data)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=actor_id,
            action="ESCALATED",
            metadata_={"reason": reason, "previous_priority": ticket.priority, "new_priority": new_priority}
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        # We could also trigger a notification here
        return updated_ticket

ticket_escalation_service = TicketEscalationService()
