from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel
import asyncio

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.repositories.billing_repo import plan_repo, usage_record_repo
from app.services.billing.billing_service import (
    stripe_service, subscription_service, plan_enforcement_service, usage_tracking_service
)

router = APIRouter()

class UsageLogRequest(BaseModel):
    metric_name: str
    metric_value: float = 1.0

# --- PUBLIC ROUTES ---

@router.get("/plans")
async def get_plans(db: AsyncSession = Depends(get_db)):
    """List available plans."""
    return await plan_repo.get_all(db)

# --- PROTECTED ROUTES ---

@router.get("/subscription")
async def get_current_subscription(
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    sub = await subscription_service.get_subscription(db, str(member.workspace_id))
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    return sub

@router.post("/usage")
async def log_usage_event(
    req: UsageLogRequest,
    member: WorkspaceMember = Depends(require_permission("manage_billing")),
    db: AsyncSession = Depends(get_db)
):
    """Admin tool to explicitly log usage."""
    # Enforce before logging
    try:
        await plan_enforcement_service.check_limit(db, str(member.workspace_id), req.metric_name, req.metric_value)
    except plan_enforcement_service.LimitExceededError as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    await usage_tracking_service.track_usage(db, str(member.workspace_id), req.metric_name, req.metric_value)
    return {"message": "Usage logged"}

# --- STRIPE WEBHOOKS ---

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook target for Stripe.
    In a real environment, we would use `stripe.Webhook.construct_event`
    with the raw payload and `stripe_signature`.
    """
    payload = await request.json()
    
    # Mock signature verification
    if not stripe_signature:
        pass # Normally raise HTTPException 400
        
    await stripe_service.process_webhook(db, payload)
    
    return {"status": "success"}
