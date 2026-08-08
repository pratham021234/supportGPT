from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.models.ticket import TicketStatus, TicketPriority
from app.services.ticketing.ticket_service import ticket_service, comment_service, sla_service

router = APIRouter()

class TicketCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    category: Optional[str] = None
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None

class CommentCreateRequest(BaseModel):
    content: str
    is_internal: bool = False

class TicketStatusUpdate(BaseModel):
    status: TicketStatus

class TicketAssignRequest(BaseModel):
    assigned_user_id: str

@router.post("")
async def create_ticket(
    req: TicketCreateRequest,
    member: WorkspaceMember = Depends(require_permission("create_ticket")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_service.create_ticket(
        db=db,
        workspace_id=str(member.workspace_id),
        ticket_data=req.model_dump(),
        created_by=str(member.user_id)
    )
    return ticket

@router.get("")
async def list_tickets(
    member: WorkspaceMember = Depends(require_permission("view_tickets")),
    db: AsyncSession = Depends(get_db)
):
    return await ticket_service.get_workspace_tickets(db, str(member.workspace_id))

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("view_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Append SLA status dynamically
    sla_status = await sla_service.check_sla_breach(db, ticket)
    
    # Normally we'd return a Pydantic model. For MVP brevity we can mutate or wrap.
    return {
        "ticket": ticket,
        "sla": sla_status
    }

@router.patch("/{ticket_id}/status")
async def update_status(
    ticket_id: str,
    req: TicketStatusUpdate,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_service.update_status(db, ticket_id, req.status, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/comments")
async def add_comment(
    ticket_id: str,
    req: CommentCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    comment = await comment_service.add_comment(
        db=db,
        ticket_id=ticket_id,
        author_id=str(member.user_id),
        content=req.content,
        is_internal=req.is_internal
    )
    return comment
    
@router.get("/{ticket_id}/comments")
async def get_comments(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("view_tickets")),
    db: AsyncSession = Depends(get_db)
):
    return await comment_service.get_comments(db, ticket_id)

@router.post("/setup-sla")
async def setup_sla(
    member: WorkspaceMember = Depends(require_permission("manage_sla")),
    db: AsyncSession = Depends(get_db)
):
    await sla_service.setup_default_slas(db, str(member.workspace_id))
    return {"message": "SLA rules initialized"}

@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    req: TicketAssignRequest,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_service.assign_ticket(db, ticket_id, req.assigned_user_id, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_service.update_status(db, ticket_id, TicketStatus.RESOLVED, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_service.update_status(db, ticket_id, TicketStatus.CLOSED, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
