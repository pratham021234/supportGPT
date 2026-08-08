import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class GapStatus(str, enum.Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    event_type = Column(String(100), nullable=False, index=True) # e.g. "TICKET_CREATED", "RAG_QUERY"
    entity_type = Column(String(100), nullable=True) # e.g. "TICKET", "CONVERSATION"
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    metadata_ = Column("metadata", JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    aggregation_period = Column(String(50), nullable=False) # e.g. "DAILY", "WEEKLY"
    
    snapshot_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    widget_type = Column(String(100), nullable=False) # e.g. "LINE_CHART", "KPI_CARD"
    configuration = Column(JSONB, nullable=False)
    position = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    query = Column(String(500), nullable=False)
    occurrences = Column(Integer, default=1)
    confidence_average = Column(Float, default=0.0)
    escalation_count = Column(Integer, default=0)
    
    status = Column(Enum(GapStatus), default=GapStatus.OPEN)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CostMetric(Base):
    __tablename__ = "cost_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    provider = Column(String(100), nullable=False) # e.g. "OPENAI", "ANTHROPIC"
    tokens_used = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0) # in USD
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
