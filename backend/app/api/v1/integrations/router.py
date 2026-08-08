from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from pydantic import BaseModel
import asyncio

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.repositories.integration_repo import (
    integration_conn_repo, integration_sync_repo, 
    IntegrationConnectionInternalCreate, ConnectionStatus
)
from app.services.integrations.connectors import get_connector

router = APIRouter()

class ConnectRequest(BaseModel):
    provider: str
    auth_code: str

# --- MARKETPLACE & CONNECTIONS ---

@router.get("/marketplace")
async def get_marketplace():
    """Returns available apps in the integrations marketplace."""
    return [
        {"id": "slack", "name": "Slack", "category": "Communication", "description": "Send alerts and sync conversations to Slack channels."},
        {"id": "hubspot", "name": "HubSpot", "category": "CRM", "description": "Sync tickets and contacts bidirectionally."},
        {"id": "salesforce", "name": "Salesforce", "category": "CRM", "description": "Enterprise sync for cases and accounts."},
        {"id": "zendesk", "name": "Zendesk", "category": "Helpdesk", "description": "Import historical tickets and knowledge base articles."}
    ]

@router.get("/")
async def get_active_connections(
    member: WorkspaceMember = Depends(require_permission("manage_settings")),
    db: AsyncSession = Depends(get_db)
):
    """List all active connections for this workspace."""
    return await integration_conn_repo.get_by_workspace(db, str(member.workspace_id))

@router.post("/connect")
async def connect_integration(
    req: ConnectRequest,
    member: WorkspaceMember = Depends(require_permission("manage_settings")),
    db: AsyncSession = Depends(get_db)
):
    """Exchanges an OAuth code and creates a connection."""
    try:
        connector = get_connector(req.provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unsupported provider")
        
    # Check if already connected
    existing = await integration_conn_repo.get_active_by_provider(db, str(member.workspace_id), req.provider)
    if existing:
        return {"message": "Already connected", "connection_id": existing.id}
        
    # Connect
    tokens = await connector.connect(str(member.workspace_id), req.auth_code)
    
    # Save
    conn_in = IntegrationConnectionInternalCreate(
        workspace_id=str(member.workspace_id),
        provider=req.provider,
        access_token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token")
    )
    conn = await integration_conn_repo.create(db, obj_in=conn_in)
    
    return {"message": "Connected successfully", "connection_id": conn.id}

@router.post("/{connection_id}/disconnect")
async def disconnect_integration(
    connection_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_settings")),
    db: AsyncSession = Depends(get_db)
):
    """Disconnects an app."""
    conn = await integration_conn_repo.get(db, id=connection_id)
    if not conn or str(conn.workspace_id) != str(member.workspace_id):
        raise HTTPException(status_code=404, detail="Connection not found")
        
    connector = get_connector(conn.provider)
    await connector.disconnect(str(member.workspace_id))
    
    await integration_conn_repo.update(db, db_obj=conn, obj_in={"status": ConnectionStatus.DISCONNECTED})
    
    return {"message": "Disconnected successfully"}

# --- SYNC LOGS & WEBHOOKS ---

@router.get("/logs")
async def get_sync_logs(
    member: WorkspaceMember = Depends(require_permission("manage_settings")),
    db: AsyncSession = Depends(get_db)
):
    """View synchronization history."""
    return await integration_sync_repo.get_by_workspace(db, str(member.workspace_id), limit=50)

@router.post("/webhooks/{provider}/{workspace_id}")
async def handle_incoming_webhook(
    provider: str,
    workspace_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Generic webhook receiver for third-party apps (e.g. Slack events, Zapier triggers).
    """
    try:
        connector = get_connector(provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unsupported provider")
        
    payload = await request.json()
    
    # In a real app we'd verify signatures here based on the provider
    
    await connector.handle_webhook(workspace_id, payload)
    
    return {"status": "success"}
