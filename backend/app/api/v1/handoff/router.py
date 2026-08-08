from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.models.handoff import AgentPresenceStatus
from app.services.handoff.handoff_service import presence_service, queue_service, handoff_service, ai_assist_service
from app.services.messaging.conversation_service import conversation_service

router = APIRouter()

class QueueCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    priority: int = 1

class PresenceUpdateRequest(BaseModel):
    status: AgentPresenceStatus
    
class HandoffInitiateRequest(BaseModel):
    conversation_id: str
    to_user_id: Optional[str] = None
    reason: str

@router.get("/agent-console/dashboard")
async def get_dashboard(
    member: WorkspaceMember = Depends(require_permission("join_conversations")),
    db: AsyncSession = Depends(get_db)
):
    # Stub: return active conversations where is_human_active is True or it's assigned to this user
    return {"message": "Dashboard ready"}

@router.post("/agents/status")
async def update_presence(
    req: PresenceUpdateRequest,
    member: WorkspaceMember = Depends(require_permission("join_conversations")),
    db: AsyncSession = Depends(get_db)
):
    presence = await presence_service.update_status(db, str(member.workspace_id), str(member.user_id), req.status)
    return presence

@router.get("/agents/presence")
async def get_team_presence(
    member: WorkspaceMember = Depends(require_permission("view_agent_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await presence_service.get_workspace_presence(db, str(member.workspace_id))

@router.post("/queues")
async def create_queue(
    req: QueueCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_queues")),
    db: AsyncSession = Depends(get_db)
):
    queue = await queue_service.create_queue(
        db, str(member.workspace_id), req.name, req.description, req.priority
    )
    return queue

@router.post("/handoff/initiate")
async def initiate_handoff(
    req: HandoffInitiateRequest,
    member: WorkspaceMember = Depends(require_permission("takeover_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.get_conversation(db, req.conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    handoff = await handoff_service.initiate_handoff(
        db, req.conversation_id, str(conv.agent_id) if conv.agent_id else None, req.to_user_id, req.reason, "USER"
    )
    return handoff

@router.post("/handoff/{conversation_id}/accept")
async def accept_handoff(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("takeover_conversations")),
    db: AsyncSession = Depends(get_db)
):
    success = await handoff_service.accept_handoff(db, conversation_id, str(member.user_id))
    if not success:
        raise HTTPException(status_code=400, detail="Failed to accept handoff")
    return {"message": "Handoff accepted"}
    
@router.post("/handoff/{conversation_id}/release")
async def release_handoff(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("takeover_conversations")),
    db: AsyncSession = Depends(get_db)
):
    success = await handoff_service.release_handoff(db, conversation_id, str(member.user_id))
    if not success:
        raise HTTPException(status_code=400, detail="Failed to release handoff")
    return {"message": "Handoff released"}

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("join_conversations")),
    db: AsyncSession = Depends(get_db)
):
    summary = await ai_assist_service.generate_summary(db, conversation_id)
    return {"summary": summary}
