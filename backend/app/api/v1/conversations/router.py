from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.models.conversation import ConversationStatus, SenderType, MessageType
from app.services.messaging.conversation_service import conversation_service, customer_service
from app.services.messaging.realtime_service import realtime_messaging_service
from app.services.messaging.websocket_manager import websocket_manager
from app.services.messaging.conversation_engine import conversation_engine
from app.services.messaging.message_service import message_service
from app.services.messaging.conversation_search_service import conversation_search_service
from app.services.handoff.human_handoff_service import human_handoff_service
from app.services.ticketing.ticket_creation_service import ticket_creation_service
from app.schemas.common import PaginationParams, FilterParams, PaginatedResponse
from app.services.billing.billing_service import plan_enforcement_service, usage_tracking_service
import json

router = APIRouter()

class CustomerCreateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class ConversationCreateRequest(BaseModel):
    customer_id: str
    agent_id: Optional[str] = None

class MessageCreateRequest(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    is_internal: bool = False
    metadata_: Optional[dict] = None

class ConversationAssignRequest(BaseModel):
    assigned_user_id: str

class ConversationEscalateRequest(BaseModel):
    reason: str

class FeedbackCreateRequest(BaseModel):
    is_helpful: Optional[bool] = None
    rating: Optional[int] = None
    comment: Optional[str] = None

class TagCreateRequest(BaseModel):
    tag: str

@router.post("/customers")
async def create_or_get_customer(
    req: CustomerCreateRequest,
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    customer = await customer_service.get_or_create_customer(
        db=db,
        workspace_id=str(member.workspace_id),
        email=req.email,
        name=req.name
    )
    return customer

@router.post("")
async def create_conversation(
    req: ConversationCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    try:
        await plan_enforcement_service.check_limit(db, str(member.workspace_id), "conversations", 1.0)
    except plan_enforcement_service.LimitExceededError as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    conv = await conversation_engine.create_conversation(
        db=db,
        workspace_id=str(member.workspace_id),
        customer_id=req.customer_id,
        agent_id=req.agent_id
    )
    await usage_tracking_service.track_usage(db, str(member.workspace_id), "conversations", 1.0)
    return conv

@router.get("", response_model=PaginatedResponse[Any])
async def list_conversations(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    return await conversation_service.get_workspace_conversations_paginated(
        db, 
        str(member.workspace_id),
        pagination,
        filters
    )

@router.get("/search")
async def search_conversations(
    query: str,
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    return await conversation_search_service.search_conversations(db, str(member.workspace_id), query)

@router.get("/analytics")
async def get_conversation_analytics(
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import func, select
    from app.models.conversation import Conversation
    
    workspace_id = str(member.workspace_id)
    
    # Very basic aggregation for MVP
    stmt = select(
        func.count(Conversation.id).label("total_conversations"),
        func.count(Conversation.id).filter(Conversation.status != ConversationStatus.CLOSED).filter(Conversation.status != ConversationStatus.RESOLVED).label("open_conversations"),
        func.count(Conversation.id).filter(Conversation.status == ConversationStatus.RESOLVED).label("resolved_conversations"),
        func.count(Conversation.id).filter(Conversation.status == ConversationStatus.ESCALATED).label("escalations")
    ).where(Conversation.workspace_id == workspace_id)
    
    res = await db.execute(stmt)
    row = res.one()
    
    total = row.total_conversations or 0
    resolved = row.resolved_conversations or 0
    
    return {
        "total_conversations": total,
        "open_conversations": row.open_conversations or 0,
        "resolved_conversations": resolved,
        "escalations": row.escalations or 0,
        "average_resolution_time_mins": 45.2, # Mocked metric for MVP
        "ai_resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0.0
    }

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    messages = await message_service.get_messages(db, conversation_id)
    return messages

@router.post("/{conversation_id}/message")
async def add_manual_message(
    conversation_id: str,
    req: MessageCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    sender = SenderType.SYSTEM if req.is_internal else SenderType.AGENT
    msg = await message_service.store_message(
        db=db,
        conversation_id=conversation_id,
        sender_type=sender,
        content=req.content,
        sender_id=str(member.user_id),
        message_type=req.message_type,
        metadata_=req.metadata_
    )
    
    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
        "type": "message",
        "sender": sender.value,
        "content": req.content,
        "is_internal": req.is_internal,
        "metadata": req.metadata_
    })
    
    return msg

@router.post("/{conversation_id}/assign")
async def assign_conversation(
    conversation_id: str,
    req: ConversationAssignRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_engine.transfer_conversation(db, conversation_id, req.assigned_user_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
        "type": "system_event",
        "content": "Conversation assigned to a new agent."
    })
    
    return conv

@router.post("/{conversation_id}/escalate")
async def escalate_conversation(
    conversation_id: str,
    req: ConversationEscalateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await human_handoff_service.trigger_handoff(
        db=db,
        conversation_id=conversation_id,
        reason=req.reason,
        initiated_by=str(member.user_id),
        from_agent_id=str(conv.agent_id) if conv.agent_id else None
    )
    
    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
        "type": "system_event",
        "content": "Conversation escalated."
    })
    return {"status": "Escalated"}

@router.post("/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_engine.update_conversation(db, conversation_id, {"status": ConversationStatus.RESOLVED})
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
        "type": "system_event",
        "content": "Conversation marked as resolved."
    })
    return conv

@router.post("/{conversation_id}/close")
async def close_conversation(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_engine.close_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
        "type": "system_event",
        "content": "Conversation closed."
    })
    return conv

@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_engine.archive_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return conv

@router.post("/{conversation_id}/tags")
async def tag_conversation(
    conversation_id: str,
    req: TagCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.add_tag(db, conversation_id, req.tag)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return conv

@router.post("/{conversation_id}/feedback")
async def submit_feedback(
    conversation_id: str,
    req: FeedbackCreateRequest,
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    fb = await conversation_service.add_feedback(
        db=db,
        conversation_id=conversation_id,
        is_helpful=req.is_helpful,
        rating=req.rating,
        comment=req.comment
    )
    return fb

@router.websocket("/{conversation_id}/ws")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str, db: AsyncSession = Depends(get_db)):
    await websocket_manager.connect(websocket, "chat", conversation_id)
    dummy_user_id = "00000000-0000-0000-0000-000000000000" 
    try:
        while True:
            data = await websocket.receive_text()
            await realtime_messaging_service.handle_customer_message(
                db=db,
                websocket=websocket,
                conversation_id=conversation_id,
                text=data,
                user_id=dummy_user_id
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "chat", conversation_id)

@router.websocket("/agent/{user_id}/ws")
async def agent_websocket_endpoint(websocket: WebSocket, user_id: str, db: AsyncSession = Depends(get_db)):
    await websocket_manager.connect(websocket, "agent", user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Agent sends messages through this socket
            msg_data = json.loads(data)
            conv_id = msg_data.get("conversation_id")
            text = msg_data.get("content")
            if conv_id and text:
                await realtime_messaging_service.handle_agent_message(
                    db=db,
                    conversation_id=conv_id,
                    text=text,
                    user_id=user_id
                )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "agent", user_id)

@router.websocket("/notifications/{user_id}/ws")
async def notifications_websocket_endpoint(websocket: WebSocket, user_id: str, db: AsyncSession = Depends(get_db)):
    await websocket_manager.connect(websocket, "notifications", user_id)
    try:
        while True:
            await websocket.receive_text() # keepalive
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "notifications", user_id)
