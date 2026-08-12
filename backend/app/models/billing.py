import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin

class SubscriptionStatus(str, enum.Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"

class BillingCycle(str, enum.Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAID = "PAID"
    VOID = "VOID"
    FAILED = "FAILED"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class SeatStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Plan(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "billing_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    monthly_price = Column(Float, default=0.0)
    annual_price = Column(Float, default=0.0)
    
    # JSON array of string features
    features = Column(JSONB, default=list)
    # JSON dict of limits (e.g. {"max_agents": 5, "max_conversations": 5000})
    limits = Column(JSONB, default=dict)

class Subscription(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "billing_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("billing_plans.id", ondelete="RESTRICT"), nullable=False)
    
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    
    # Stripe mapping
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    renews_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

class PaymentMethod(Base, TimestampMixin):
    __tablename__ = "billing_payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    provider = Column(String(50), default="stripe")
    provider_reference = Column(String(255), nullable=False) # pm_xxx

class Invoice(Base, TimestampMixin):
    __tablename__ = "billing_invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("billing_subscriptions.id", ondelete="SET NULL"), nullable=True)
    
    invoice_number = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    issued_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    paid_at = Column(DateTime(timezone=True), nullable=True)

class Payment(Base, TimestampMixin):
    __tablename__ = "billing_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("billing_invoices.id", ondelete="CASCADE"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    provider_reference = Column(String(255), nullable=True) # pi_xxx
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

class Seat(Base, TimestampMixin):
    __tablename__ = "billing_seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(Enum(SeatStatus), default=SeatStatus.ACTIVE)

class UsageRecord(Base, TimestampMixin):
    __tablename__ = "billing_usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    metric_name = Column(String(100), nullable=False, index=True) # e.g. "conversations", "prompt_tokens"
    metric_value = Column(Float, default=1.0)
    
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
