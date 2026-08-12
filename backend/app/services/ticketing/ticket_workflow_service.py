import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from app.repositories.ticket_repo import ticket_repo, ticket_activity_repo, TicketActivityInternalCreate
from app.models.ticket import Ticket, TicketStatus

logger = logging.getLogger(__name__)

class TicketWorkflowService:
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
        
        return updated_ticket

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
        
        return updated_ticket

ticket_workflow_service = TicketWorkflowService()
