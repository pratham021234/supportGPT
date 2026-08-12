from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel

from app.dependencies import (
    get_db, get_current_active_user, get_current_workspace,
    require_workspace_member, require_workspace_admin, require_workspace_owner
)
from app.services import workspace_service, invitation_service, audit_service, team_service
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse,
    WorkspaceMemberResponse, WorkspaceMemberUpdate,
    WorkspaceInvitationCreate, WorkspaceInvitationResponse, AcceptInvitationRequest,
    WorkspaceAuditLogResponse
)
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

class SwitchWorkspaceRequest(BaseModel):
    workspace_id: str

@router.post("", response_model=Dict[str, Any])
async def create_workspace(request: WorkspaceCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    workspace = await workspace_service.create_workspace(db, current_user, request)
    return {
        "success": True,
        "message": "Workspace created successfully",
        "data": WorkspaceResponse.model_validate(workspace).model_dump()
    }

@router.get("", response_model=Dict[str, Any])
async def list_workspaces(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    workspaces = await workspace_service.get_user_workspaces(db, str(current_user.id))
    return {
        "success": True,
        "message": "Workspaces fetched successfully",
        "data": [WorkspaceResponse.model_validate(w).model_dump() for w in workspaces]
    }

@router.post("/switch", response_model=Dict[str, Any])
async def switch_workspace(request: SwitchWorkspaceRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    workspace = await workspace_service.switch_workspace(db, current_user, request.workspace_id)
    return {
        "success": True,
        "message": f"Switched to workspace {workspace.name}",
        "data": WorkspaceResponse.model_validate(workspace).model_dump()
    }

@router.get("/current", response_model=Dict[str, Any])
async def get_current_active_workspace(workspace: Workspace = Depends(get_current_workspace)):
    return {
        "success": True,
        "message": "Current workspace fetched successfully",
        "data": WorkspaceResponse.model_validate(workspace).model_dump()
    }

@router.get("/{id}", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_member)])
async def get_workspace(id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    workspace = await workspace_service.get_workspace(db, id, str(current_user.id))
    return {
        "success": True,
        "message": "Workspace fetched successfully",
        "data": WorkspaceResponse.model_validate(workspace).model_dump()
    }

@router.patch("/{id}", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_admin)])
async def update_workspace(id: str, request: WorkspaceUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    workspace = await workspace_service.update_settings(db, id, request, str(current_user.id))
    return {
        "success": True,
        "message": "Workspace updated successfully",
        "data": WorkspaceResponse.model_validate(workspace).model_dump()
    }

@router.delete("/{id}", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_owner)])
async def delete_workspace(id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    await workspace_service.delete_workspace(db, id, str(current_user.id))
    return {
        "success": True,
        "message": "Workspace deleted successfully"
    }

@router.get("/{id}/members", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_member)])
async def list_members(id: str, db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    members = await team_service.get_members(db, id, skip, limit)
    # Map to schema mapping user email/name optionally
    data = []
    for m in members:
        schema = WorkspaceMemberResponse.model_validate(m)
        if getattr(m, 'user', None):
            schema.user_email = m.user.email
            schema.user_full_name = m.user.full_name
        data.append(schema.model_dump())
        
    return {
        "success": True,
        "data": data
    }

@router.patch("/{id}/members/{member_id}", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_admin)])
async def change_member_role(id: str, member_id: str, request: WorkspaceMemberUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # request.role is probably a role name or ID. If ID, team_service.assign_role_by_id. If name, assign_role.
    # Assuming role name from schema
    assignment = await team_service.assign_role(db, member_id, request.role, str(current_user.id))
    # We might need to fetch the updated member
    updated_member = await team_service.get_member(db, id, member_id)
    return {
        "success": True,
        "message": "Member role updated",
        "data": WorkspaceMemberResponse.model_validate(updated_member).model_dump()
    }

@router.delete("/{id}/members/{member_id}", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_admin)])
async def remove_member(id: str, member_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    await team_service.update_status(db, id, member_id, "REMOVED", str(current_user.id))
    return {
        "success": True,
        "message": "Member removed successfully"
    }

@router.post("/{id}/invite", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_admin)])
async def invite_member(id: str, request: WorkspaceInvitationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    invitation = await invitation_service.invite_member(db, id, request, str(current_user.id))
    return {
        "success": True,
        "message": f"Invitation sent to {request.email}",
        "data": WorkspaceInvitationResponse.model_validate(invitation).model_dump()
    }

@router.get("/invitations/pending", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_admin)])
async def list_invitations(workspace: Workspace = Depends(get_current_workspace), db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    invitations = await invitation_service.get_invitations(db, str(workspace.id), skip, limit)
    return {
        "success": True,
        "data": [WorkspaceInvitationResponse.model_validate(i).model_dump() for i in invitations]
    }

@router.post("/invitations/accept", response_model=Dict[str, Any])
async def accept_invitation(request: AcceptInvitationRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    await invitation_service.accept_invitation(db, str(current_user.id), request.token)
    return {
        "success": True,
        "message": "Invitation accepted successfully"
    }

@router.get("/{id}/audit-logs", response_model=Dict[str, Any], dependencies=[Depends(require_workspace_admin)])
async def get_audit_logs(id: str, db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    logs = await audit_service.get_workspace_logs(db, id, skip, limit)
    return {
        "success": True,
        "data": [WorkspaceAuditLogResponse.model_validate(log).model_dump() for log in logs]
    }
