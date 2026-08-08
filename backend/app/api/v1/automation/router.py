from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional, Dict
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.repositories.automation_repo import (
    automation_rule_repo, workflow_execution_repo, webhook_endpoint_repo,
    AutomationRuleInternalCreate, WebhookEndpointInternalCreate, RuleStatus
)

router = APIRouter()

class RuleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_event: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]

class WebhookCreateRequest(BaseModel):
    name: str
    url: str
    secret: Optional[str] = None

# --- AUTOMATION RULES ---

@router.get("/rules")
async def get_rules(
    member: WorkspaceMember = Depends(require_permission("manage_automation")),
    db: AsyncSession = Depends(get_db)
):
    return await automation_rule_repo.get_by_workspace(db, str(member.workspace_id))

@router.post("/rules")
async def create_rule(
    req: RuleCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_automation")),
    db: AsyncSession = Depends(get_db)
):
    rule_in = AutomationRuleInternalCreate(
        workspace_id=str(member.workspace_id),
        name=req.name,
        description=req.description,
        trigger_event=req.trigger_event,
        conditions=req.conditions,
        actions=req.actions
    )
    return await automation_rule_repo.create(db, obj_in=rule_in)

@router.delete("/rules/{id}")
async def delete_rule(
    id: str,
    member: WorkspaceMember = Depends(require_permission("manage_automation")),
    db: AsyncSession = Depends(get_db)
):
    rule = await automation_rule_repo.get(db, id=id)
    if not rule or str(rule.workspace_id) != str(member.workspace_id):
        raise HTTPException(status_code=404, detail="Rule not found")
        
    await automation_rule_repo.delete(db, id=id)
    return {"message": "Rule deleted"}

# --- WORKFLOW EXECUTIONS ---

@router.get("/executions")
async def get_executions(
    member: WorkspaceMember = Depends(require_permission("manage_automation")),
    db: AsyncSession = Depends(get_db)
):
    return await workflow_execution_repo.get_by_workspace(db, str(member.workspace_id))

# --- WEBHOOKS ---

@router.get("/webhooks")
async def get_webhooks(
    member: WorkspaceMember = Depends(require_permission("manage_automation")),
    db: AsyncSession = Depends(get_db)
):
    return await webhook_endpoint_repo.get_active_by_workspace(db, str(member.workspace_id))

@router.post("/webhooks")
async def create_webhook(
    req: WebhookCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_automation")),
    db: AsyncSession = Depends(get_db)
):
    wh_in = WebhookEndpointInternalCreate(
        workspace_id=str(member.workspace_id),
        name=req.name,
        url=req.url,
        secret=req.secret
    )
    return await webhook_endpoint_repo.create(db, obj_in=wh_in)
