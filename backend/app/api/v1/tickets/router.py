from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.models.ticket import TicketStatus, TicketPriority
from app.services.ticketing.ticket_creation_service import ticket_creation_service
from app.services.ticketing.ticket_workflow_service import ticket_workflow_service
from app.services.ticketing.sla_service import sla_service
from app.services.ticketing.internal_note_service import internal_note_service
from app.repositories.ticket_repo import ticket_repo
from app.schemas.common import PaginationParams, FilterParams, PaginatedResponse

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

class TicketUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = None

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
    ticket = await ticket_creation_service.create_ticket(
        db=db,
        workspace_id=str(member.workspace_id),
        ticket_data=req.model_dump(),
        created_by=str(member.user_id)
    )
    return ticket

@router.get("", response_model=PaginatedResponse[Any])
async def list_tickets(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    member: WorkspaceMember = Depends(require_permission("view_tickets")),
    db: AsyncSession = Depends(get_db)
):
    return await ticket_repo.get_paginated(db, pagination=pagination, filters=filters, workspace_id=str(member.workspace_id))

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("view_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_repo.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    sla_status = await sla_service.check_sla_breach(db, ticket)
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
    ticket = await ticket_workflow_service.update_status(db, ticket_id, req.status, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    req: TicketUpdateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_repo.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    updated_ticket = await ticket_repo.update(db, db_obj=ticket, obj_in=req.model_dump(exclude_unset=True))
    return updated_ticket

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_repo.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await ticket_repo.remove(db, id=ticket_id)
    return {"message": "Ticket deleted"}

@router.post("/{ticket_id}/comments")
async def add_comment(
    ticket_id: str,
    req: CommentCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    if req.is_internal:
        comment = await internal_note_service.add_private_note(
            db=db,
            ticket_id=ticket_id,
            author_id=str(member.user_id),
            content=req.content
        )
    else:
        # Public comments handled by ticket_comment_repo
        from app.repositories.ticket_repo import ticket_comment_repo, TicketCommentInternalCreate
        comment = await ticket_comment_repo.create(db, obj_in=TicketCommentInternalCreate(
            ticket_id=ticket_id,
            author_id=str(member.user_id),
            content=req.content,
            is_internal=False
        ))
    return comment
    
@router.get("/{ticket_id}/comments")
async def get_comments(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("view_tickets")),
    db: AsyncSession = Depends(get_db)
):
    from app.repositories.ticket_repo import ticket_comment_repo
    return await ticket_comment_repo.get_by_ticket(db, ticket_id)

@router.post("/setup-sla")
async def setup_sla(
    tier: str = "silver",
    member: WorkspaceMember = Depends(require_permission("manage_sla")),
    db: AsyncSession = Depends(get_db)
):
    await sla_service.setup_slas(db, str(member.workspace_id), tier)
    return {"message": f"SLA rules initialized for tier: {tier}"}

@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    req: TicketAssignRequest,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_workflow_service.assign_ticket(db, ticket_id, req.assigned_user_id, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_workflow_service.update_status(db, ticket_id, TicketStatus.RESOLVED, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_tickets")),
    db: AsyncSession = Depends(get_db)
):
    ticket = await ticket_workflow_service.update_status(db, ticket_id, TicketStatus.CLOSED, str(member.user_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
