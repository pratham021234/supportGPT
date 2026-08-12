import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.repositories.billing_repo import (
    plan_repo, subscription_repo, usage_record_repo, invoice_repo,
    Plan, Subscription, UsageRecord, Invoice,
    SubscriptionStatus, UsageRecordInternalCreate, InvoiceInternalCreate, InvoiceStatus
)
from app.services.notifications.notification_service import event_bus

logger = logging.getLogger(__name__)

class StripeService:
    """Mocks interaction with Stripe API."""
    
    async def create_checkout_session(self, db: AsyncSession, workspace_id: str, plan_id: str) -> str:
        """Mocks returning a Stripe checkout session URL."""
        # Validate plan exists
        plan = await plan_repo.get(db, id=plan_id)
        if not plan:
            raise ValueError("Invalid Plan ID")
            
        return f"https://mock-stripe.com/checkout/cs_test_{uuid.uuid4().hex[:16]}"
        
    async def create_customer_portal(self, db: AsyncSession, workspace_id: str) -> str:
        """Mocks returning a Stripe customer portal URL."""
        return f"https://mock-stripe.com/portal/session_test_{uuid.uuid4().hex[:16]}"
        
    async def cancel_subscription(self, db: AsyncSession, workspace_id: str):
        sub = await subscription_repo.get_by_workspace(db, workspace_id)
        if sub:
            await subscription_repo.update(db, db_obj=sub, obj_in={
                "status": SubscriptionStatus.CANCELLED,
                "cancelled_at": datetime.utcnow()
            })
            await event_bus.publish(db, workspace_id, "SUBSCRIPTION_CANCELLED")
    
    async def process_webhook(self, db: AsyncSession, payload: dict):
        event_type = payload.get("type")
        data = payload.get("data", {}).get("object", {})
        
        logger.info(f"Processing Stripe Webhook: {event_type}")
        
        if event_type == "checkout.session.completed":
            workspace_id = data.get("client_reference_id")
            stripe_sub_id = data.get("subscription", f"sub_{uuid.uuid4().hex[:12]}")
            stripe_cust_id = data.get("customer", f"cus_{uuid.uuid4().hex[:12]}")
            
            if workspace_id:
                sub = await subscription_repo.get_by_workspace(db, workspace_id)
                if sub:
                    updates = {
                        "status": SubscriptionStatus.ACTIVE,
                        "stripe_subscription_id": stripe_sub_id,
                        "stripe_customer_id": stripe_cust_id,
                        "renews_at": datetime.utcnow() # mock future date
                    }
                    await subscription_repo.update(db, db_obj=sub, obj_in=updates)
                    
                    # Create an initial paid invoice for records
                    inv_in = InvoiceInternalCreate(
                        workspace_id=workspace_id,
                        subscription_id=str(sub.id),
                        invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                        amount=99.0, # mock amount
                        status=InvoiceStatus.PAID,
                        paid_at=datetime.utcnow()
                    )
                    await invoice_repo.create(db, obj_in=inv_in)
                    
                    # Fire event
                    await event_bus.publish(db, workspace_id, "SUBSCRIPTION_ACTIVATED")
                    
        elif event_type == "invoice.payment_failed":
            stripe_sub_id = data.get("subscription")
            if stripe_sub_id:
                # Mock lookup by stripe_sub_id
                # In real app: sub = await subscription_repo.get_by_stripe_id(db, stripe_sub_id)
                pass
                
        elif event_type == "customer.subscription.deleted":
            stripe_sub_id = data.get("id")
            pass

class UsageTrackingService:
    async def track_usage(self, db: AsyncSession, workspace_id: str, metric_name: str, value: float = 1.0):
        """Standard usage logging."""
        usage_in = UsageRecordInternalCreate(
            workspace_id=workspace_id,
            metric_name=metric_name,
            metric_value=value
        )
        await usage_record_repo.create(db, obj_in=usage_in)
        
    async def get_usage_summary(self, db: AsyncSession, workspace_id: str) -> Dict[str, Any]:
        """Returns current usage against plan limits."""
        sub = await subscription_repo.get_by_workspace(db, workspace_id)
        if not sub:
            return {"usage": {}, "limits": {}}
            
        plan = await plan_repo.get(db, id=str(sub.plan_id))
        
        # We'll just hardcode two metrics for MVP Dashboard
        metrics_to_track = ["conversations", "agents"]
        
        usage = {}
        for m in metrics_to_track:
            usage[m] = await usage_record_repo.get_usage_sum(db, workspace_id, m)
            
        return {
            "usage": usage,
            "limits": plan.limits if plan else {}
        }

class PlanEnforcementService:
    class LimitExceededError(Exception):
        pass

    async def check_limit(self, db: AsyncSession, workspace_id: str, metric_name: str, increment: float = 1.0):
        """Checks if incrementing the metric would exceed the plan limits. Throws LimitExceededError if breached."""
        sub = await subscription_repo.get_by_workspace(db, workspace_id)
        if not sub:
            raise self.LimitExceededError("No active subscription found.")
            
        plan = await plan_repo.get(db, id=str(sub.plan_id))
        if not plan:
            raise self.LimitExceededError("Invalid plan.")
            
        limit = plan.limits.get(metric_name)
        if limit is None:
            # No limit imposed
            return True
            
        # Get current sum
        current_usage = await usage_record_repo.get_usage_sum(db, workspace_id, metric_name)
        if (current_usage + increment) > limit:
            raise self.LimitExceededError(f"Plan limit for {metric_name} exceeded (limit: {limit}). Upgrade your plan.")
            
        return True

class SubscriptionService:
    async def get_subscription(self, db: AsyncSession, workspace_id: str) -> Optional[Subscription]:
        return await subscription_repo.get_by_workspace(db, workspace_id)

class PlanService:
    async def seed_default_plans(self, db: AsyncSession):
        plans_data = [
            {
                "name": "Free",
                "monthly_price": 0.0,
                "limits": {"agents": 1, "conversations": 100, "documents": 10},
                "features": []
            },
            {
                "name": "Pro",
                "monthly_price": 49.0,
                "limits": {"agents": 5, "conversations": 5000, "documents": 500},
                "features": ["advanced_analytics"]
            },
            {
                "name": "Business",
                "monthly_price": 199.0,
                "limits": {"agents": 999999, "conversations": 50000, "documents": 5000},
                "features": ["advanced_analytics", "priority_support"]
            },
            {
                "name": "Enterprise",
                "monthly_price": 999.0,
                "limits": {"agents": 999999, "conversations": 999999, "documents": 999999},
                "features": ["advanced_analytics", "priority_support", "sso", "custom_models"]
            }
        ]
        
        for p_data in plans_data:
            # Upsert logic normally goes here, we'll mock creation
            plan = Plan(**p_data)
            db.add(plan)
        await db.commit()

class FeatureGateService:
    async def has_feature(self, db: AsyncSession, workspace_id: str, feature_key: str) -> bool:
        sub = await subscription_repo.get_by_workspace(db, workspace_id)
        if not sub:
            return False
        plan = await plan_repo.get(db, id=str(sub.plan_id))
        if not plan:
            return False
        return feature_key in plan.features

class RevenueAnalyticsService:
    async def get_mrr(self, db: AsyncSession) -> float:
        # Simplistic MRR sum based on active subscriptions
        stmt = select(Subscription, Plan).join(Plan, Subscription.plan_id == Plan.id).where(Subscription.status == SubscriptionStatus.ACTIVE)
        result = await db.execute(stmt)
        rows = result.all()
        
        mrr = 0.0
        for sub, plan in rows:
            if sub.billing_cycle == BillingCycle.MONTHLY:
                mrr += plan.monthly_price
            else:
                mrr += (plan.annual_price / 12)
        return mrr

stripe_service = StripeService()
usage_tracking_service = UsageTrackingService()
plan_enforcement_service = PlanEnforcementService()
subscription_service = SubscriptionService()
plan_service = PlanService()
feature_gate_service = FeatureGateService()
revenue_analytics_service = RevenueAnalyticsService()
