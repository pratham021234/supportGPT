from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel
import asyncio
import json

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.notifications.notification_service import (
    event_bus, notification_service, preference_service
)
from app.schemas.common import PaginationParams, FilterParams, PaginatedResponse
from app.services.messaging.websocket_manager import websocket_manager

router = APIRouter()

class EventPublishRequest(BaseModel):
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    payload: Optional[dict] = None

class PreferenceUpdateRequest(BaseModel):
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    digest_enabled: Optional[bool] = None

@router.post("/events")
async def publish_event(
    req: EventPublishRequest,
    member: WorkspaceMember = Depends(require_permission("manage_alerts")), # System level, mocked
    db: AsyncSession = Depends(get_db)
):
    await event_bus.publish(
        db, str(member.workspace_id), req.event_type, req.entity_type, req.entity_id, str(member.user_id), req.payload
    )
    return {"message": "Event published"}

@router.get("/", response_model=PaginatedResponse[Any])
async def list_notifications(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    member: WorkspaceMember = Depends(require_permission("view_notifications")),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.get_user_notifications_paginated(db, str(member.user_id), pagination, filters)

@router.get("/unread")
async def get_unread_notifications(
    member: WorkspaceMember = Depends(require_permission("view_notifications")),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.get_unread(db, str(member.user_id))

@router.patch("/{id}/read")
async def mark_notification_read(
    id: str,
    member: WorkspaceMember = Depends(require_permission("view_notifications")),
    db: AsyncSession = Depends(get_db)
):
    notif = await notification_service.mark_as_read(db, id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Marked as read"}

@router.post("/read-all")
async def mark_all_read(
    member: WorkspaceMember = Depends(require_permission("view_notifications")),
    db: AsyncSession = Depends(get_db)
):
    await notification_service.mark_all_read(db, str(member.user_id))
    return {"message": "All notifications marked as read"}

@router.get("/health")
async def get_health(
    member: WorkspaceMember = Depends(require_permission("manage_alerts")),
    db: AsyncSession = Depends(get_db)
):
    from app.services.notifications.notification_health_service import notification_health_service
    return await notification_health_service.get_health_metrics(db)

@router.delete("/{id}")
async def delete_notification(
    id: str,
    member: WorkspaceMember = Depends(require_permission("view_notifications")),
    db: AsyncSession = Depends(get_db)
):
    success = await notification_service.delete_notification(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}

@router.get("/preferences")
async def get_preferences(
    member: WorkspaceMember = Depends(require_permission("view_notifications")),
    db: AsyncSession = Depends(get_db)
):
    return await preference_service.get_preferences(db, str(member.user_id))
    
@router.patch("/preferences")
async def update_preferences(
    req: PreferenceUpdateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_notification_preferences")),
    db: AsyncSession = Depends(get_db)
):
    updates = {k: v for k, v in req.dict().items() if v is not None}
    pref = await preference_service.update_preferences(db, str(member.user_id), updates)
    return pref

@router.websocket("/ws")
async def websocket_notifications(
    websocket: WebSocket,
    # member: WorkspaceMember = Depends(require_permission("view_notifications")) # Auth needs to be handled via token query param for WebSockets usually, but we'll assume user_id is passed as query param for MVP
    user_id: str
):
    await websocket_manager.connect(websocket, "notifications", user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Notifications are usually one-way server-to-client, but we can acknowledge
            await websocket.send_text(json.dumps({"status": "connected", "received": data}))
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "notifications", user_id)
