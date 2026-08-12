from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.workspace_service import workspace_service
from app.schemas.workspace import WorkspaceResponse

router = APIRouter()

class SettingsUpdateRequest(BaseModel):
    branding: Optional[Dict[str, Any]] = None
    ai: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None

@router.get("")
async def get_settings(
    member: WorkspaceMember = Depends(require_permission("view_settings")),
    db: AsyncSession = Depends(get_db)
):
    workspace = await workspace_service.get_workspace(db, str(member.workspace_id), str(member.user_id))
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"settings": workspace.settings or {}}

@router.patch("")
async def update_settings(
    req: SettingsUpdateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_settings")),
    db: AsyncSession = Depends(get_db)
):
    workspace = await workspace_service.get_workspace(db, str(member.workspace_id), str(member.user_id))
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    current_settings = workspace.settings or {}
    
    if req.branding is not None:
        current_settings["branding"] = req.branding
    if req.ai is not None:
        current_settings["ai"] = req.ai
    if req.notifications is not None:
        current_settings["notifications"] = req.notifications
    if req.security is not None:
        current_settings["security"] = req.security
        
    # Hack to use existing service
    from app.schemas.workspace import WorkspaceUpdate
    update_req = WorkspaceUpdate(settings=current_settings)
    updated_workspace = await workspace_service.update_settings(db, str(member.workspace_id), update_req, str(member.user_id))
    
    return {"settings": updated_workspace.settings}
