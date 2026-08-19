import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from app.repositories.ticket_repo import (
    ticket_repo, ticket_comment_repo, ticket_activity_repo, sla_repo,
    TicketInternalCreate, TicketCommentInternalCreate, TicketActivityInternalCreate, SLAConfigurationInternalCreate
)
from app.models.ticket import Ticket, TicketComment, TicketPriority, TicketStatus, TicketSource
from app.services.analytics.analytics_service import analytics_event_service

logger = logging.getLogger(__name__)

class TicketService:
    async def create_ticket(self, db: AsyncSession, workspace_id: str, ticket_data: Dict[str, Any], created_by: Optional[str] = None) -> Ticket:
        ticket_in = TicketInternalCreate(
            workspace_id=workspace_id,
            created_by=created_by,
            **ticket_data
        )
        ticket = await ticket_repo.create(db, obj_in=ticket_in)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=str(ticket.id),
            actor_id=created_by,
            action="TICKET_CREATED"
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        await analytics_event_service.log_event(
            db=db,
            workspace_id=workspace_id,
            event_type="TICKET_CREATED",
            entity_type="TICKET",
            entity_id=str(ticket.id)
        )
        
        return ticket
        
    async def get_workspace_tickets_paginated(self, db: AsyncSession, workspace_id: str, pagination: Any, filters: Any):
        return await ticket_repo.get_paginated(db, pagination=pagination, filters=filters, workspace_id=workspace_id)

    async def get_workspace_tickets(self, db: AsyncSession, workspace_id: str):
        return await ticket_repo.get_by_workspace(db, workspace_id=workspace_id)

    async def get_ticket(self, db: AsyncSession, ticket_id: str) -> Optional[Ticket]:
        return await ticket_repo.get(db, id=ticket_id)

    async def update_status(self, db: AsyncSession, ticket_id: str, status: TicketStatus, actor_id: str) -> Optional[Ticket]:
        ticket = await ticket_repo.get(db, id=ticket_id)
        if not ticket:
            return None
            
        update_data = {"status": status}
        if status == TicketStatus.RESOLVED:
            update_data["resolved_at"] = datetime.utcnow()
            update_data["resolved_by"] = actor_id
        elif status == TicketStatus.CLOSED:
            update_data["closed_at"] = datetime.utcnow()
            
        updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in=update_data)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=actor_id,
            action=f"STATUS_CHANGED_TO_{status.value}"
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        if status == TicketStatus.RESOLVED:
            await analytics_event_service.log_event(
                db=db,
                workspace_id=str(ticket.workspace_id),
                event_type="TICKET_RESOLVED",
                entity_type="TICKET",
                entity_id=ticket_id,
                metadata_={"resolved_by": actor_id}
            )
        
        return updated_ticket

    async def update_ticket(self, db: AsyncSession, ticket_id: str, update_data: Dict[str, Any], actor_id: str) -> Optional[Ticket]:
        ticket = await ticket_repo.get(db, id=ticket_id)
        if not ticket:
            return None
            
        updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in=update_data)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=actor_id,
            action="TICKET_UPDATED",
            metadata_=update_data
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        return updated_ticket

    async def delete_ticket(self, db: AsyncSession, ticket_id: str) -> bool:
        ticket = await ticket_repo.get(db, id=ticket_id)
        if not ticket:
            return False
            
        await ticket_repo.remove(db, id=ticket_id)
        return True

    async def assign_ticket(self, db: AsyncSession, ticket_id: str, assigned_user_id: str, actor_id: str) -> Optional[Ticket]:
        ticket = await ticket_repo.get(db, id=ticket_id)
        if not ticket:
            return None
            
        updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in={"assigned_to": assigned_user_id})
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=actor_id,
            action="ASSIGNED",
            metadata_={"assigned_user_id": assigned_user_id}
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        await analytics_event_service.log_event(
            db=db,
            workspace_id=str(ticket.workspace_id),
            event_type="TICKET_ASSIGNED",
            entity_type="TICKET",
            entity_id=ticket_id,
            metadata_={"assigned_user_id": assigned_user_id, "actor_id": actor_id}
        )
        
        return updated_ticket

    async def create_ai_escalation(self, db: AsyncSession, workspace_id: str, conversation_id: str, customer_id: str, reason: str) -> Ticket:
        """Called by the RAG Engine when confidence is low."""
        ticket_in = TicketInternalCreate(
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
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
        return ticket


class CommentService:
    async def add_comment(self, db: AsyncSession, ticket_id: str, author_id: str, content: str, is_internal: bool = False) -> TicketComment:
        comment_in = TicketCommentInternalCreate(
            ticket_id=ticket_id,
            author_id=author_id,
            content=content,
            is_internal=is_internal
        )
        comment = await ticket_comment_repo.create(db, obj_in=comment_in)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=author_id,
            action="COMMENT_ADDED",
            metadata_={"is_internal": is_internal}
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        return comment

    async def get_comments(self, db: AsyncSession, ticket_id: str):
        return await ticket_comment_repo.get_by_ticket(db, ticket_id)


class SLAService:
    async def setup_default_slas(self, db: AsyncSession, workspace_id: str):
        defaults = [
            (TicketPriority.URGENT, 60, 240),
            (TicketPriority.HIGH, 120, 480),
            (TicketPriority.MEDIUM, 480, 1440),
            (TicketPriority.LOW, 1440, 2880),
        ]
        
        for priority, first_response, resolution in defaults:
            sla_in = SLAConfigurationInternalCreate(
                workspace_id=workspace_id,
                priority=priority,
                first_response_minutes=first_response,
                resolution_minutes=resolution
            )
            await sla_repo.create(db, obj_in=sla_in)
            
    async def check_sla_breach(self, db: AsyncSession, ticket: Ticket) -> Dict[str, Any]:
        """Calculates if the ticket is breaching SLA on the fly."""
        slas = await sla_repo.get_by_workspace(db, str(ticket.workspace_id))
        
        # Find matching SLA
        config = next((s for s in slas if s.priority == ticket.priority), None)
        if not config:
            return {"first_response_breached": False, "resolution_breached": False}
            
        now = datetime.utcnow()
        elapsed_minutes = (now - ticket.created_at.replace(tzinfo=None)).total_seconds() / 60
        
        first_response_breached = False
        # We would check if there is at least one external comment by an agent.
        # For simplicity, if elapsed > first_response_minutes, it's breached.
        if elapsed_minutes > config.first_response_minutes:
            first_response_breached = True
            
        resolution_breached = False
        if ticket.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            if elapsed_minutes > config.resolution_minutes:
                resolution_breached = True
                
        return {
            "first_response_breached": first_response_breached,
            "resolution_breached": resolution_breached
        }

ticket_service = TicketService()
comment_service = CommentService()
sla_service = SLAService()
