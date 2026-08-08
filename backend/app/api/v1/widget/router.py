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

router = APIRouter()

class SessionInitRequest(BaseModel):
    workspace_id: str
    agent_id: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None

class ConversationStartRequest(BaseModel):
    session_token: str

class ConfigurationUpdateRequest(BaseModel):
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
    launcher_text: Optional[str] = None
    welcome_message: Optional[str] = None
    position: Optional[str] = None

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
            "border_radius": "8px"
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
    # In a full prod system, we would query `WorkspaceDomains` table to check if `origin` is allowed.
    if origin and "malicious-site.com" in origin:
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
        conv_id = await widget_session_service.start_conversation(db, req.session_token)
        return {"conversation_id": conv_id}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

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
