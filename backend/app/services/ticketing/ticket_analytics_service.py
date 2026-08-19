import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import Dict, Any

from app.models.ticket import Ticket, TicketStatus

logger = logging.getLogger(__name__)

class TicketAnalyticsService:
    async def get_analytics(self, db: AsyncSession, workspace_id: str) -> Dict[str, Any]:
        # Basic aggregations
        stmt = select(
            func.count(Ticket.id).label("total"),
            func.count(Ticket.id).filter(Ticket.status == TicketStatus.OPEN).label("open"),
            func.count(Ticket.id).filter(Ticket.status == TicketStatus.RESOLVED).label("resolved"),
            func.count(Ticket.id).filter(Ticket.status == TicketStatus.ESCALATED).label("escalated")
        ).where(Ticket.workspace_id == workspace_id)
        
        res = await db.execute(stmt)
        row = res.one()
        
        total = row.total or 0
        resolved = row.resolved or 0
        
        # In a real system, we'd average the diff between created_at and resolved_at
        avg_resolution_time_mins = 120.5
        sla_compliance_rate = 95.0
        
        return {
            "total_tickets": total,
            "open_tickets": row.open or 0,
            "resolved_tickets": resolved,
            "escalated_tickets": row.escalated or 0,
            "average_resolution_time_mins": avg_resolution_time_mins,
            "sla_compliance_rate": sla_compliance_rate
        }

    async def get_knowledge_gaps(self, db: AsyncSession, workspace_id: str) -> Dict[str, Any]:
        """Feedback loop to see which topics create the most tickets."""
        # Simple placeholder that would aggregate common tags or topics from escalated AI tickets
        return {
            "top_ticket_drivers": ["billing", "api", "refund"],
            "unanswered_questions_count": 42
        }

ticket_analytics_service = TicketAnalyticsService()
