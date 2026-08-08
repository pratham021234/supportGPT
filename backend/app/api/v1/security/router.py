from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.security_service import (
    api_key_service, security_monitoring, compliance_service
)
from app.services.audit_service import audit_service
from app.repositories.session_repo import user_session_repo

router = APIRouter()

class ApiKeyCreate(BaseModel):
    name: str
    scopes: List[str]

# --- API KEYS ---

@router.get("/api-keys")
async def get_api_keys(
    member: WorkspaceMember = Depends(require_permission("manage_security")),
    db: AsyncSession = Depends(get_db)
):
    return await api_key_service.get_by_workspace(db, str(member.workspace_id))

@router.post("/api-keys")
async def create_api_key(
    req: ApiKeyCreate,
    member: WorkspaceMember = Depends(require_permission("manage_security")),
    db: AsyncSession = Depends(get_db)
):
    db_key, raw_key = await api_key_service.create_key(
        db, str(member.workspace_id), str(member.user_id), req.name, req.scopes
    )
    
    await audit_service.log_action(db, str(member.workspace_id), "API_KEY_CREATED", "ApiKey", str(member.user_id), str(db_key.id))
    
    return {"key_id": db_key.id, "raw_key": raw_key, "name": db_key.name}

@router.delete("/api-keys/{id}")
async def revoke_api_key(
    id: str,
    member: WorkspaceMember = Depends(require_permission("manage_security")),
    db: AsyncSession = Depends(get_db)
):
    await api_key_service.revoke_key(db, id)
    await audit_service.log_action(db, str(member.workspace_id), "API_KEY_REVOKED", "ApiKey", str(member.user_id), id)
    return {"message": "Key revoked"}

# --- SECURITY ALERTS ---

@router.get("/alerts")
async def get_security_alerts(
    member: WorkspaceMember = Depends(require_permission("manage_security")),
    db: AsyncSession = Depends(get_db)
):
    return await security_monitoring.get_alerts(db, str(member.workspace_id))

# --- SESSION MANAGEMENT ---

@router.get("/sessions")
async def get_active_sessions(
    member: WorkspaceMember = Depends(require_permission("manage_security")),
    db: AsyncSession = Depends(get_db)
):
    # In a real app this might only return sessions for a specific user, or all workspace sessions if admin
    return await user_session_repo.get_active_by_user(db, str(member.user_id))
    
@router.delete("/sessions/{id}")
async def revoke_session(
    id: str,
    member: WorkspaceMember = Depends(require_permission("manage_security")),
    db: AsyncSession = Depends(get_db)
):
    session = await user_session_repo.get(db, id=id)
    if session:
        await user_session_repo.update(db, db_obj=session, obj_in={"is_revoked": True})
        await audit_service.log_action(db, str(member.workspace_id), "SESSION_REVOKED", "UserSession", str(member.user_id), id)
    return {"message": "Session revoked"}

# --- COMPLIANCE (GDPR) ---

@router.post("/compliance/export")
async def export_my_data(
    member: WorkspaceMember = Depends(require_permission("export_data")),
    db: AsyncSession = Depends(get_db)
):
    data = await compliance_service.export_user_data(db, str(member.user_id), str(member.workspace_id))
    await audit_service.log_action(db, str(member.workspace_id), "GDPR_EXPORT_REQUESTED", "User", str(member.user_id), str(member.user_id))
    return data

@router.post("/compliance/delete")
async def delete_my_account(
    background_tasks: BackgroundTasks,
    member: WorkspaceMember = Depends(require_permission("export_data")), # any user can delete themselves
    db: AsyncSession = Depends(get_db)
):
    # Enqueue hard deletion to prevent blocking
    background_tasks.add_task(compliance_service.delete_user_data, db, str(member.user_id))
    await audit_service.log_action(db, str(member.workspace_id), "GDPR_DELETION_REQUESTED", "User", str(member.user_id), str(member.user_id))
    return {"message": "Account deletion queued"}
