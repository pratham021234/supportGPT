import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.models.conversation import Customer
from app.repositories.conversation_repo import customer_repo
from app.repositories.conversation_repo import conversation_repo
from app.repositories.ticket_repo import ticket_repo

logger = logging.getLogger(__name__)

class CustomerProfileService:
    async def get_customer_profile(self, db: AsyncSession, workspace_id: str, customer_id: str) -> Dict[str, Any]:
        """Fetches customer details along with conversation and ticket history."""
        customer = await customer_repo.get(db, id=customer_id)
        if not customer or str(customer.workspace_id) != workspace_id:
            return {}
            
        conversations = await conversation_repo.get_by_workspace(db, workspace_id=workspace_id)
        customer_conversations = [c for c in conversations if str(c.customer_id) == customer_id]
        
        tickets = await ticket_repo.get_by_workspace(db, workspace_id=workspace_id)
        customer_tickets = [t for t in tickets if str(t.customer_id) == customer_id]
        
        return {
            "profile": {
                "id": str(customer.id),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "external_id": customer.external_id,
                "first_seen_at": customer.first_seen_at,
                "last_seen_at": customer.last_seen_at
            },
            "history": {
                "total_conversations": len(customer_conversations),
                "total_tickets": len(customer_tickets),
                "recent_conversations": [
                    {"id": str(c.id), "status": c.status, "started_at": c.started_at}
                    for c in sorted(customer_conversations, key=lambda x: x.started_at or x.created_at, reverse=True)[:5]
                ]
            }
        }

customer_profile_service = CustomerProfileService()
