from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories import workspace_repo, workspace_member_repo
from app.core.exceptions import UnauthorizedException, ForbiddenException, NotFoundException, BadRequestException

async def get_current_workspace(
    x_workspace_id: Optional[str] = Header(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Workspace:
    """
    Resolves the current workspace context.
    If x-workspace-id header is provided, it uses that (after verifying membership).
    Otherwise, it defaults to the user's active_workspace_id.
    """
    target_workspace_id = x_workspace_id or current_user.active_workspace_id
    
    if not target_workspace_id:
        raise BadRequestException("No active workspace found and no workspace ID provided in headers")

    workspace = await workspace_repo.get(db, id=target_workspace_id)
    if not workspace:
        raise NotFoundException("Workspace not found")
        
    return workspace

async def require_workspace_member(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceMember:
    """
    Ensures the user is a member of the resolved workspace.
    """
    member = await workspace_member_repo.get_by_workspace_and_user(
        db, workspace_id=str(workspace.id), user_id=str(current_user.id)
    )
    if not member:
        raise ForbiddenException("You are not a member of this workspace")
    return member

def require_workspace_role(allowed_roles: list[str]):
    async def role_checker(
        member: WorkspaceMember = Depends(require_workspace_member)
    ) -> WorkspaceMember:
        if member.role not in allowed_roles and member.role != "OWNER":
            raise ForbiddenException(f"Workspace role must be one of {allowed_roles}")
        return member
    return role_checker

require_workspace_owner = require_workspace_role(["OWNER"])
require_workspace_admin = require_workspace_role(["ADMIN", "OWNER"])
require_workspace_support = require_workspace_role(["SUPPORT_AGENT", "ADMIN", "OWNER"])
