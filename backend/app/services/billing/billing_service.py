import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from app.repositories.billing_repo import (
    plan_repo, subscription_repo, usage_record_repo,
    Plan, Subscription, UsageRecord,
    SubscriptionStatus, UsageRecordInternalCreate
)
from app.services.notifications.notification_service import event_bus

logger = logging.getLogger(__name__)

class StripeService:
    """Mocks interaction with Stripe API and parses webhooks."""
    
    async def process_webhook(self, db: AsyncSession, payload: dict):
        event_type = payload.get("type")
        data = payload.get("data", {}).get("object", {})
        
        logger.info(f"Processing Stripe Webhook: {event_type}")
        
        if event_type == "checkout.session.completed":
            workspace_id = data.get("client_reference_id")
            stripe_sub_id = data.get("subscription")
            stripe_cust_id = data.get("customer")
            
            if workspace_id:
                sub = await subscription_repo.get_by_workspace(db, workspace_id)
                if sub:
                    updates = {
                        "status": SubscriptionStatus.ACTIVE,
                        "stripe_subscription_id": stripe_sub_id,
                        "stripe_customer_id": stripe_cust_id
                    }
                    await subscription_repo.update(db, db_obj=sub, obj_in=updates)
                    
                    # Fire event
                    await event_bus.publish(db, workspace_id, "SUBSCRIPTION_ACTIVATED")
                    
        elif event_type == "customer.subscription.deleted":
            stripe_sub_id = data.get("id")
            # In a real app we'd query by stripe_subscription_id
            # We'll mock this lookup for MVP
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

stripe_service = StripeService()
usage_tracking_service = UsageTrackingService()
plan_enforcement_service = PlanEnforcementService()
subscription_service = SubscriptionService()
