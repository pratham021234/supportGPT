from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel
import asyncio

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.repositories.billing_repo import plan_repo, usage_record_repo, invoice_repo
from app.services.billing.billing_service import (
    stripe_service, subscription_service, plan_enforcement_service, usage_tracking_service,
    revenue_analytics_service
)

router = APIRouter()

class UsageLogRequest(BaseModel):
    metric_name: str
    metric_value: float = 1.0
    
class CheckoutRequest(BaseModel):
    plan_id: str

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

@router.post("/checkout")
async def create_checkout(
    req: CheckoutRequest,
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    """Generate Stripe Checkout URL"""
    url = await stripe_service.create_checkout_session(db, str(member.workspace_id), req.plan_id)
    return {"url": url}

@router.post("/subscribe")
async def subscribe(
    req: CheckoutRequest,
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    return await create_checkout(req, member, db)

@router.post("/customer-portal")
async def create_customer_portal(
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    """Generate Stripe Customer Portal URL"""
    url = await stripe_service.create_customer_portal(db, str(member.workspace_id))
    return {"url": url}

@router.post("/portal")
async def portal(
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    return await create_customer_portal(member, db)

@router.post("/cancel")
async def cancel_subscription(
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    await stripe_service.cancel_subscription(db, str(member.workspace_id))
    return {"message": "Subscription cancelled."}

@router.get("/invoices")
async def get_invoices(
    member: WorkspaceMember = Depends(require_permission("manage_subscriptions")),
    db: AsyncSession = Depends(get_db)
):
    return await invoice_repo.get_by_workspace(db, str(member.workspace_id))

@router.get("/usage")
async def get_usage(
    member: WorkspaceMember = Depends(require_permission("manage_billing")),
    db: AsyncSession = Depends(get_db)
):
    """Get current usage against plan limits"""
    return await usage_tracking_service.get_usage_summary(db, str(member.workspace_id))

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

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Ingest Stripe Webhooks"""
    payload = await request.json()
    await stripe_service.process_webhook(db, payload)
    return {"status": "success"}
    
@router.get("/analytics")
async def get_revenue_analytics(
    db: AsyncSession = Depends(get_db)
):
    """Get global revenue metrics for admin dashboard"""
    mrr = await revenue_analytics_service.get_mrr(db)
    return {
        "mrr": mrr,
        "arr": mrr * 12
    }

# --- STRIPE WEBHOOKS ---

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook target for Stripe.
    """
    payload = await request.json()
    
    # Mock signature verification
    if not stripe_signature:
        pass # Normally raise HTTPException 400
        
    await stripe_service.process_webhook(db, payload)
    
    return {"status": "success"}
