from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.repositories.base import BaseRepository
from app.models.billing import (
    Plan, Subscription, PaymentMethod, Invoice, Payment, Seat, UsageRecord,
    SubscriptionStatus, BillingCycle
)
from pydantic import BaseModel
from datetime import datetime

class PlanInternalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    monthly_price: float = 0.0
    annual_price: float = 0.0
    features: List[str] = []
    limits: Dict[str, Any] = {}

class SubscriptionInternalCreate(BaseModel):
    workspace_id: str
    plan_id: str
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    renews_at: Optional[datetime] = None

class UsageRecordInternalCreate(BaseModel):
    workspace_id: str
    metric_name: str
    metric_value: float = 1.0

class InvoiceInternalCreate(BaseModel):
    workspace_id: str
    amount_due: float
    amount_paid: float
    status: str
    stripe_invoice_id: Optional[str] = None

class PlanRepository(BaseRepository[Plan, PlanInternalCreate, BaseModel]):
    pass

class SubscriptionRepository(BaseRepository[Subscription, SubscriptionInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> Optional[Subscription]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class UsageRecordRepository(BaseRepository[UsageRecord, UsageRecordInternalCreate, BaseModel]):
    async def get_usage_sum(self, db: AsyncSession, workspace_id: str, metric_name: str) -> float:
        """Helper to get the total aggregated usage for a metric."""
        query = select(func.sum(self.model.metric_value)).where(
            self.model.workspace_id == workspace_id,
            self.model.metric_name == metric_name
        )
        result = await db.execute(query)
        return result.scalar() or 0.0

class InvoiceRepository(BaseRepository[Invoice, InvoiceInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[Invoice]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return list(result.scalars().all())

plan_repo = PlanRepository(Plan)
subscription_repo = SubscriptionRepository(Subscription)
usage_record_repo = UsageRecordRepository(UsageRecord)
invoice_repo = InvoiceRepository(Invoice)
