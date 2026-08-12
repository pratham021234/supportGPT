import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from app.repositories.ticket_repo import sla_repo, SLAConfigurationInternalCreate
from app.models.ticket import Ticket, TicketPriority, TicketStatus

logger = logging.getLogger(__name__)

class SLAService:
    async def setup_slas(self, db: AsyncSession, workspace_id: str, tier: str = "silver"):
        """
        Setup default SLAs based on the tier.
        Tiers: gold, silver, enterprise
        """
        
        # Define SLA tiers in minutes (First Response, Resolution)
        sla_matrix = {
            "silver": {
                TicketPriority.URGENT: (60, 240),
                TicketPriority.HIGH: (120, 480),
                TicketPriority.MEDIUM: (480, 1440),
                TicketPriority.LOW: (1440, 2880)
            },
            "gold": {
                TicketPriority.URGENT: (30, 120),
                TicketPriority.HIGH: (60, 240),
                TicketPriority.MEDIUM: (240, 720),
                TicketPriority.LOW: (720, 1440)
            },
            "enterprise": {
                TicketPriority.URGENT: (15, 60),
                TicketPriority.HIGH: (30, 120),
                TicketPriority.MEDIUM: (60, 240),
                TicketPriority.LOW: (240, 480)
            }
        }
        
        selected_tier = sla_matrix.get(tier.lower(), sla_matrix["silver"])
        
        for priority, (first_response, resolution) in selected_tier.items():
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

sla_service = SLAService()
