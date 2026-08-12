from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from pydantic import BaseModel
import uuid

from app.dependencies.db import get_db
from app.services.organization_service import (
    workspace_management_service,
    invitation_service,
    audit_log_service
)

router = APIRouter()

class OrganizationCreateRequest(BaseModel):
    name: str
    slug: str

class WorkspaceCreateRequest(BaseModel):
    name: str
    slug: str
    organization_id: str

class InviteMemberRequest(BaseModel):
    email: str
    role: str
    workspace_id: str

@router.post("")
async def create_organization(
    req: OrganizationCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    from app.models.organization import Organization
    org = Organization(
        id=uuid.uuid4(),
        name=req.name,
        slug=req.slug,
        owner_id=uuid.uuid4() # Mocked owner for testing
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org

@router.get("")
async def get_organizations():
    return [{"id": "org1", "name": "Acme Inc"}]

@router.post("/workspaces")
async def create_workspace(
    req: WorkspaceCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    ws = await workspace_management_service.create_workspace(
        db, req.organization_id, str(uuid.uuid4()), {"name": req.name, "slug": req.slug}
    )
    return ws

@router.get("/workspaces")
async def get_workspaces():
    return [{"id": "ws1", "name": "Support Team"}]

@router.post("/members/invite")
async def invite_member(
    req: InviteMemberRequest,
    db: AsyncSession = Depends(get_db)
):
    invite = await invitation_service.invite_member(
        db, req.workspace_id, str(uuid.uuid4()), req.email, req.role
    )
    return invite
    
@router.get("/audit-logs")
async def get_audit_logs():
    return [{"action": "LOGIN", "actor": "user1"}]
