from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class TimestampMixin:
    """Mixin for models that need created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditMixin:
    """Mixin for models that need to track who created/updated a record."""
    # Note: the foreign keys point to users.id but as strings or UUID depending on setup.
    # In this app, users.id is UUID(as_uuid=True).
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

class SoftDeleteMixin:
    """Mixin for soft-deletable records."""
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
