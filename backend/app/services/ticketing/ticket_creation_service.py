import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import uuid

from app.repositories.ticket_repo import ticket_repo, ticket_activity_repo, TicketInternalCreate, TicketActivityInternalCreate
from app.models.ticket import Ticket, TicketPriority, TicketSource
from app.services.notifications.notification_service import event_bus

logger = logging.getLogger(__name__)

class TicketCreationService:
    async def create_ticket(self, db: AsyncSession, workspace_id: str, ticket_data: Dict[str, Any], created_by: Optional[str] = None) -> Ticket:
        ticket_number = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        ticket_in = TicketInternalCreate(
            workspace_id=workspace_id,
            created_by=created_by,
            ticket_number=ticket_number,
            **ticket_data
        )
        ticket = await ticket_repo.create(db, obj_in=ticket_in)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=str(ticket.id),
            actor_id=created_by,
            action="TICKET_CREATED"
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        await event_bus.publish(
            db=db,
            workspace_id=str(ticket.workspace_id),
            event_type="TICKET_CREATED",
            entity_type="TICKET",
            entity_id=str(ticket.id),
            actor_id=created_by,
            payload={
                "ticket_id": str(ticket.id),
                "title": ticket.title,
                "priority": ticket.priority.value
            }
        )
        
        return ticket

    async def create_ai_escalation(self, db: AsyncSession, workspace_id: str, conversation_id: str, customer_id: str, reason: str) -> Ticket:
        """Called by the EscalationEngine when confidence is low or human is requested."""
        ticket_number = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        ticket_in = TicketInternalCreate(
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            ticket_number=ticket_number,
            title=f"AI Escalation for Conv {str(conversation_id)[:8]}",
            description=reason,
            priority=TicketPriority.MEDIUM,
            source=TicketSource.AI_ESCALATION
        )
        ticket = await ticket_repo.create(db, obj_in=ticket_in)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=str(ticket.id),
            action="AI_ESCALATION_CREATED"
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        await event_bus.publish(
            db=db,
            workspace_id=str(ticket.workspace_id),
            event_type="TICKET_ESCALATED",
            entity_type="TICKET",
            entity_id=str(ticket.id),
            payload={
                "ticket_id": str(ticket.id),
                "title": ticket.title,
                "reason": reason
            }
        )
        
        return ticket

ticket_creation_service = TicketCreationService()
