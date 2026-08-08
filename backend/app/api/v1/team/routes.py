from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel
import uuid

from app.dependencies import (
    get_db, get_current_active_user, get_current_workspace,
    require_workspace_member, require_permission, require_workspace_owner
)
from app.services import team_service, invitation_service, audit_service
from app.schemas.team import (
    TeamMemberResponse, AssignRoleRequest, UpdateMemberStatusRequest, TransferOwnershipRequest, RoleResponse, PermissionResponse
)
from app.schemas.workspace import WorkspaceInvitationCreate, WorkspaceInvitationResponse
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories import role_repo, permission_repo

router = APIRouter(prefix="/team", tags=["team"])

@router.get("/members", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_member)])
async def list_members(workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    members = await team_service.get_members(db, str(workspace.id), skip, limit)
    data = []
    for m in members:
        schema = TeamMemberResponse.model_validate(m)
        if getattr(m, 'user', None):
            schema.user_email = m.user.email
            schema.user_full_name = m.user.full_name
        # Roles are attached via m.roles (which are UserWorkspaceRole records, containing .role)
        # We need to map them properly in the schema mapping step. 
        # The schema uses from_attributes=True, so it should map nested relationships natively.
        data.append(schema.model_dump())
        
    return {
        "success": True,
        "data": data
    }

@router.get("/members/{id}", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_member)])
async def get_member(id: str, workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    member = await team_service.get_member(db, str(workspace.id), id)
    schema = TeamMemberResponse.model_validate(member)
    if getattr(member, 'user', None):
        schema.user_email = member.user.email
        schema.user_full_name = member.user.full_name
    return {
        "success": True,
        "data": schema.model_dump()
    }

@router.post("/invite", response_model=Dict[str, Any], dependencies=[Depends(require_permission("manage_team"))])
async def invite_member(request: WorkspaceInvitationCreate, workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    invitation = await invitation_service.invite_member(db, str(workspace.id), request, str(current_user.id))
    return {
        "success": True,
        "message": f"Invitation sent to {request.email}",
        "data": WorkspaceInvitationResponse.model_validate(invitation).model_dump()
    }

@router.patch("/members/{id}/role", response_model=Dict[str, Any], dependencies=[Depends(require_permission("manage_team"))])
async def assign_role(id: str, request: AssignRoleRequest, workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    assignment = await team_service.assign_role_by_id(db, str(workspace.id), id, str(request.role_id), str(current_user.id))
    return {
        "success": True,
        "message": "Role assigned successfully"
    }

@router.patch("/members/{id}/status", response_model=Dict[str, Any], dependencies=[Depends(require_permission("manage_team"))])
async def update_member_status(id: str, request: UpdateMemberStatusRequest, workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    member = await team_service.update_status(db, str(workspace.id), id, request.status, str(current_user.id))
    return {
        "success": True,
        "message": f"Member status updated to {request.status}",
        "data": TeamMemberResponse.model_validate(member).model_dump()
    }

@router.post("/transfer-ownership", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_owner)])
async def transfer_ownership(request: TransferOwnershipRequest, current_member: WorkspaceMember = Depends(require_workspace_owner), workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    await team_service.transfer_ownership(db, str(workspace.id), str(current_member.id), str(request.new_owner_member_id))
    return {
        "success": True,
        "message": "Workspace ownership transferred successfully"
    }

@router.get("/roles", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_member)])
async def list_roles(workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    roles = await role_repo.get_workspace_roles(db, str(workspace.id))
    return {
        "success": True,
        "data": [RoleResponse.model_validate(r).model_dump() for r in roles]
    }

@router.get("/permissions", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_member)])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    permissions = await permission_repo.get_all(db)
    return {
        "success": True,
        "data": [PermissionResponse.model_validate(p).model_dump() for p in permissions]
    }
