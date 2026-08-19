from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel
import asyncio
import json

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.widget.widget_service import (
    widget_config_service, widget_session_service
)
from app.services.billing.billing_service import plan_enforcement_service

router = APIRouter()

class SessionInitRequest(BaseModel):
    workspace_id: str
    agent_id: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None

class ConversationStartRequest(BaseModel):
    session_token: str

class WidgetMessageRequest(BaseModel):
    session_token: str
    content: str

class ConfigurationUpdateRequest(BaseModel):
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
    launcher_text: Optional[str] = None
    welcome_message: Optional[str] = None
    position: Optional[str] = None
    allowed_domains: Optional[List[str]] = None
    suggested_questions: Optional[List[str]] = None
    offline_message: Optional[str] = None
    support_hours: Optional[dict] = None

class WidgetTicketRequest(BaseModel):
    session_token: str
    reason: str

class WidgetHandoffRequest(BaseModel):
    session_token: str

# --- PUBLIC ROUTES ---

@router.get("/config/{agent_id}")
async def get_public_config(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Public endpoint called by the javascript bundle on load."""
    config = await widget_config_service.get_configuration(db, agent_id)
    if not config:
        # Provide sensible defaults if they haven't configured it yet
        return {
            "theme": "light",
            "primary_color": "#000000",
            "launcher_text": "Chat with us",
            "welcome_message": "Hello! How can I help you today?",
            "position": "bottom-right",
            "border_radius": "8px",
            "allowed_domains": [],
            "suggested_questions": [],
            "offline_message": "We are currently offline. Please leave a message or create a ticket.",
            "support_hours": {}
        }
    return config

@router.post("/session")
async def initialize_session(
    req: SessionInitRequest,
    origin: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Generates an anonymous or identified session for a visitor."""
    # Origin validation for multi-site deployment security
    if origin:
        config = await widget_config_service.get_configuration(db, req.agent_id)
        if config and config.allowed_domains:
            # Simple check if origin is in allowed domains
            allowed = False
            for domain in config.allowed_domains:
                if domain in origin:
                    allowed = True
                    break
            if not allowed:
                raise HTTPException(status_code=403, detail="Origin not authorized for this widget.")
        
    # We can pass customer details if identify() was called prior to initialization
    # If customer is already known, we look them up or create them. 
    # For simplicity, we just pass None for now and let start_conversation create "Anonymous Visitor"
    # unless email is provided.
    customer_id = None
    if req.customer_email:
        from app.repositories.conversation_repo import customer_repo, CustomerInternalCreate
        # Lookup existing customer or create
        existing = await customer_repo.get_by_email(db, req.workspace_id, req.customer_email)
        if existing:
            customer_id = str(existing.id)
        else:
            cust_in = CustomerInternalCreate(
                workspace_id=req.workspace_id,
                name=req.customer_name or "Known Customer",
                email=req.customer_email
            )
            cust = await customer_repo.create(db, obj_in=cust_in)
            customer_id = str(cust.id)
            
    session = await widget_session_service.initialize_session(
        db, req.workspace_id, req.agent_id, customer_id=customer_id
    )
    return {"session_token": session.session_token}

@router.post("/conversations")
async def start_conversation(
    req: ConversationStartRequest,
    db: AsyncSession = Depends(get_db)
):
    """Converts a widget session into a backend Conversation ID"""
    try:
        session = await widget_session_service.get_session(db, req.session_token)
        if session:
            try:
                await plan_enforcement_service.check_limit(db, str(session.workspace_id), "conversations", 1.0)
            except plan_enforcement_service.LimitExceededError as e:
                raise HTTPException(status_code=402, detail=str(e))
                
        conv_id = await widget_session_service.start_conversation(db, req.session_token)
        return {"conversation_id": conv_id}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/message")
async def send_widget_message(
    req: WidgetMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Anonymous message endpoint for widget SDK."""
    session = await widget_session_service.get_session(db, req.session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    from app.services.messaging.message_service import message_service
    # Needs a conversation to be started
    # For MVP, we auto-start if no active conversation is mapped in session. 
    # But WidgetSession doesn't store active conversation ID, so we query it via customer_id.
    from app.repositories.conversation_repo import conversation_repo
    convs = await conversation_repo.get_by_workspace(db, str(session.workspace_id))
    # Filter by customer_id
    active_conv = next((c for c in convs if str(c.customer_id) == str(session.customer_id)), None)
    
    if not active_conv:
        conv_id = await widget_session_service.start_conversation(db, req.session_token)
        active_conv = await conversation_repo.get(db, id=conv_id)
        
    # Send message as Customer
    # In a full impl, this would trigger RAG agent workflow. We mock a reply here for widget SDK demo.
    reply_text = f"Received your message: {req.content}. Our agents will be right with you."
    
    return {"reply": reply_text}

@router.get("/history/{session_token}")
async def get_widget_history(
    session_token: str,
    db: AsyncSession = Depends(get_db)
):
    session = await widget_session_service.get_session(db, session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    from app.repositories.conversation_repo import conversation_repo, message_repo
    convs = await conversation_repo.get_by_workspace(db, str(session.workspace_id))
    active_conv = next((c for c in convs if str(c.customer_id) == str(session.customer_id)), None)
    
    if not active_conv:
        return {"messages": []}
        
    msgs = await message_repo.get_by_conversation(db, str(active_conv.id))
    return {
        "messages": [
            {"id": str(m.id), "content": m.content, "sender_type": m.sender_type.value, "created_at": m.created_at.isoformat()}
            for m in msgs
        ]
    }

@router.post("/handoff")
async def handoff_conversation(
    req: WidgetHandoffRequest,
    db: AsyncSession = Depends(get_db)
):
    session = await widget_session_service.get_session(db, req.session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    # Trigger handoff in our handoff service
    # For MVP, we just return success
    return {"message": "Escalated to human"}

@router.post("/ticket")
async def convert_to_ticket(
    req: WidgetTicketRequest,
    db: AsyncSession = Depends(get_db)
):
    session = await widget_session_service.get_session(db, req.session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    from app.services.ticketing.ticket_creation_service import ticket_creation_service
    # Start conversation if it doesn't exist
    conv_id = await widget_session_service.start_conversation(db, req.session_token)
    
    ticket = await ticket_creation_service.create_ai_escalation(
        db=db,
        workspace_id=str(session.workspace_id),
        conversation_id=str(conv_id),
        customer_id=str(session.customer_id),
        reason=req.reason
    )
    return {"ticket_id": str(ticket.id), "ticket_number": ticket.ticket_number}

# --- ADMIN ROUTES ---

@router.get("/settings")
async def get_settings(
    member: WorkspaceMember = Depends(require_permission("configure_widget")),
    db: AsyncSession = Depends(get_db)
):
    """Workspace admin endpoint to get branding."""
    config = await widget_config_service.get_or_create_workspace_config(db, str(member.workspace_id))
    return config

@router.patch("/settings")
async def update_settings(
    req: ConfigurationUpdateRequest,
    member: WorkspaceMember = Depends(require_permission("configure_widget")),
    db: AsyncSession = Depends(get_db)
):
    """Workspace admin endpoint to customize branding."""
    updates = {k: v for k, v in req.dict().items() if v is not None}
    config = await widget_config_service.update_configuration(db, str(member.workspace_id), updates)
    return config

@router.get("/embed-code")
async def get_embed_code(
    member: WorkspaceMember = Depends(require_permission("configure_widget")),
    db: AsyncSession = Depends(get_db)
):
    config = await widget_config_service.get_or_create_workspace_config(db, str(member.workspace_id))
    agent_id = str(config.agent_id) if config.agent_id else "DEFAULT_AGENT"
    
    script = f"""
<!-- SupportGPT Widget -->
<script>
window.SupportGPT = {{
    workspaceId: "{member.workspace_id}",
    agentId: "{agent_id}"
}};
</script>
<script src="https://cdn.supportgpt.ai/widget.js" async defer></script>
<!-- End SupportGPT Widget -->
"""
    return {"embed_code": script.strip()}

@router.get("/health")
async def get_widget_health():
    from app.services.widget.widget_health_service import widget_health_service
    return widget_health_service.get_widget_health()
