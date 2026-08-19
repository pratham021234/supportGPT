import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional

from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.repositories.ticket_repo import ticket_repo, ticket_activity_repo, TicketActivityInternalCreate

logger = logging.getLogger(__name__)

class TicketAssignmentService:
    async def assign_ticket_manual(self, db: AsyncSession, ticket_id: str, assigned_user_id: str, actor_id: str) -> Optional[Ticket]:
        ticket = await ticket_repo.get(db, id=ticket_id)
        if not ticket:
            return None
            
        updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in={"assigned_to": assigned_user_id})
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=actor_id,
            action="ASSIGNED_MANUAL",
            metadata_={"assigned_user_id": assigned_user_id}
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        return updated_ticket

    async def auto_assign_least_active(self, db: AsyncSession, ticket: Ticket) -> Optional[str]:
        """Assigns the ticket to the agent with the fewest OPEN/IN_PROGRESS tickets in the workspace."""
        # Find all agents in workspace
        query = select(User.id).where(User.workspace_id == ticket.workspace_id)
        result = await db.execute(query)
        agents = result.scalars().all()
        
        if not agents:
            return None
            
        # Find agent with least active tickets
        # In a real app we would do a join and group_by, but for MVP:
        counts = {}
        for agent_id in agents:
            q = select(func.count(Ticket.id)).where(
                Ticket.assigned_to == agent_id,
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.ESCALATED])
            )
            r = await db.execute(q)
            counts[agent_id] = r.scalar() or 0
            
        best_agent = min(counts, key=counts.get)
        
        updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in={"assigned_to": best_agent})
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=str(ticket.id),
            actor_id=None,
            action="ASSIGNED_AUTO_LEAST_ACTIVE",
            metadata_={"assigned_user_id": str(best_agent)}
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        return str(best_agent)

ticket_assignment_service = TicketAssignmentService()
