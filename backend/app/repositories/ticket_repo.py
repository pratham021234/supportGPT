from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.ticket import (
    Ticket, TicketComment, TicketAssignment, TicketActivity, SLAConfiguration,
    TicketPriority, TicketStatus, TicketSource
)
from pydantic import BaseModel

class TicketInternalCreate(BaseModel):
    workspace_id: str
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    category: Optional[str] = None
    source: TicketSource = TicketSource.SYSTEM
    created_by: Optional[str] = None
    assigned_to: Optional[str] = None

class TicketCommentInternalCreate(BaseModel):
    ticket_id: str
    author_id: Optional[str] = None
    content: str
    is_internal: bool = False

class TicketActivityInternalCreate(BaseModel):
    ticket_id: str
    actor_id: Optional[str] = None
    action: str
    metadata_: Optional[Dict[str, Any]] = None

class SLAConfigurationInternalCreate(BaseModel):
    workspace_id: str
    priority: TicketPriority
    first_response_minutes: int
    resolution_minutes: int

class TicketRepository(BaseRepository[Ticket, TicketInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[Ticket]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id
        ).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())

class TicketCommentRepository(BaseRepository[TicketComment, TicketCommentInternalCreate, BaseModel]):
    async def get_by_ticket(self, db: AsyncSession, ticket_id: str) -> List[TicketComment]:
        query = select(self.model).where(
            self.model.ticket_id == ticket_id
        ).order_by(self.model.created_at)
        result = await db.execute(query)
        return list(result.scalars().all())

class TicketActivityRepository(BaseRepository[TicketActivity, TicketActivityInternalCreate, BaseModel]):
    pass

class SLAConfigurationRepository(BaseRepository[SLAConfiguration, SLAConfigurationInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[SLAConfiguration]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id
        )
        result = await db.execute(query)
        return list(result.scalars().all())

ticket_repo = TicketRepository(Ticket)
ticket_comment_repo = TicketCommentRepository(TicketComment)
ticket_activity_repo = TicketActivityRepository(TicketActivity)
sla_repo = SLAConfigurationRepository(SLAConfiguration)
