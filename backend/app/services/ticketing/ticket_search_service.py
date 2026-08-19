import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, cast, String, func
from typing import List, Optional, Dict, Any

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import User
from app.models.conversation import Customer

logger = logging.getLogger(__name__)

class TicketSearchService:
    async def search_tickets(
        self, 
        db: AsyncSession, 
        workspace_id: str, 
        query: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Ticket]:
        
        stmt = (
            select(Ticket)
            .outerjoin(Customer, Ticket.customer_id == Customer.id)
            .outerjoin(User, Ticket.assigned_to == User.id)
            .where(Ticket.workspace_id == workspace_id)
        )
        
        if status and status != "ALL":
            stmt = stmt.where(Ticket.status == status)
            
        if priority and priority != "ALL":
            stmt = stmt.where(Ticket.priority == priority)
            
        if assigned_to:
            stmt = stmt.where(Ticket.assigned_to == assigned_to)
            
        if tag:
            # Postgres JSONB containment: tags contains the array [tag]
            stmt = stmt.where(Ticket.tags.contains([tag]))
            
        if query:
            stmt = stmt.where(
                or_(
                    Ticket.ticket_number.ilike(f"%{query}%"),
                    Ticket.title.ilike(f"%{query}%"),
                    Ticket.description.ilike(f"%{query}%"),
                    Customer.name.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )
            
        stmt = stmt.order_by(Ticket.created_at.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()

ticket_search_service = TicketSearchService()
