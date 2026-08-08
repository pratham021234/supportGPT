from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.models.conversation import ConversationStatus
from app.services.messaging.conversation_service import conversation_service, customer_service
from app.services.messaging.realtime_service import realtime_messaging_service
from app.services.handoff.handoff_service import handoff_service
from app.services.ticketing.ticket_service import ticket_service
from app.models.conversation import SenderType, MessageType
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

class ConversationAssignRequest(BaseModel):
    assigned_user_id: str

class ConversationEscalateRequest(BaseModel):
    reason: str

class FeedbackCreateRequest(BaseModel):
    is_helpful: Optional[bool] = None
    rating: Optional[int] = None
    comment: Optional[str] = None

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
    conv = await conversation_service.create_conversation(
        db=db,
        workspace_id=str(member.workspace_id),
        customer_id=req.customer_id,
        agent_id=req.agent_id
    )
    return conv

@router.get("")
async def list_conversations(
    status: Optional[ConversationStatus] = None,
    assigned_user_id: Optional[str] = None,
    member: WorkspaceMember = Depends(require_permission("view_conversations")),
    db: AsyncSession = Depends(get_db)
):
    return await conversation_service.get_workspace_conversations(
        db, 
        str(member.workspace_id),
        status=status,
        assigned_user_id=assigned_user_id
    )

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
    messages = await conversation_service.get_messages(db, conversation_id)
    return messages

@router.post("/{conversation_id}/message")
async def add_manual_message(
    conversation_id: str,
    req: MessageCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    # Depending on internal flag we either send as SYSTEM or SUPPORT_AGENT
    sender = SenderType.SYSTEM if req.is_internal else SenderType.SUPPORT_AGENT
    msg = await conversation_service.add_message(
        db=db,
        conversation_id=conversation_id,
        sender_type=sender,
        content=req.content,
        sender_id=str(member.user_id),
        message_type=req.message_type
    )
    
    # Broadcast to WS
    await realtime_messaging_service.manager.broadcast_to_conversation(conversation_id, {
        "type": "message",
        "sender": sender.value,
        "content": req.content,
        "is_internal": req.is_internal
    })
    
    return msg

@router.post("/{conversation_id}/assign")
async def assign_conversation(
    conversation_id: str,
    req: ConversationAssignRequest,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.assign_conversation(db, conversation_id, req.assigned_user_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await realtime_messaging_service.manager.broadcast_to_conversation(conversation_id, {
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
        
    await conversation_service.update_status(db, conversation_id, ConversationStatus.ESCALATED)
    
    await handoff_service.initiate_handoff(
        db=db,
        conversation_id=conversation_id,
        from_agent_id=str(conv.agent_id) if conv.agent_id else None,
        to_user_id=None,
        reason=req.reason,
        initiated_by=str(member.user_id)
    )
    
    ticket = await ticket_service.create_ai_escalation(
        db=db,
        workspace_id=str(conv.workspace_id),
        conversation_id=conversation_id,
        customer_id=str(conv.customer_id),
        reason=req.reason
    )
    
    await realtime_messaging_service.manager.broadcast_to_conversation(conversation_id, {
        "type": "system_event",
        "content": "Conversation escalated."
    })
    return {"status": "Escalated", "ticket_id": str(ticket.id)}

@router.post("/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_conversations")),
    db: AsyncSession = Depends(get_db)
):
    conv = await conversation_service.update_status(db, conversation_id, ConversationStatus.RESOLVED)
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await realtime_messaging_service.manager.broadcast_to_conversation(conversation_id, {
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
    conv = await conversation_service.update_status(db, conversation_id, ConversationStatus.CLOSED)
    if not conv:
        raise HTTPException(404, "Conversation not found")
        
    await realtime_messaging_service.manager.broadcast_to_conversation(conversation_id, {
        "type": "system_event",
        "content": "Conversation closed."
    })
    return conv

@router.post("/{conversation_id}/feedback")
async def submit_feedback(
    conversation_id: str,
    req: FeedbackCreateRequest,
    member: WorkspaceMember = Depends(require_permission("view_conversations")), # In reality this would be public/customer scoped
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
    """
    WebSocket endpoint for real-time messaging.
    In a real app, we'd authenticate the WebSocket using a token in query params.
    For this MVP, we assume the connection is valid and pass a dummy user_id for RAG execution.
    """
    await realtime_messaging_service.manager.connect(websocket, conversation_id)
    # Using a dummy user_id for the MVP WebSocket stream to bypass RBAC on the background RAG call
    dummy_user_id = "00000000-0000-0000-0000-000000000000" 
    
    try:
        while True:
            data = await websocket.receive_text()
            # Expecting raw text messages from the client
            await realtime_messaging_service.handle_customer_message(
                db=db,
                websocket=websocket,
                conversation_id=conversation_id,
                text=data,
                user_id=dummy_user_id
            )
    except WebSocketDisconnect:
        realtime_messaging_service.manager.disconnect(websocket, conversation_id)
