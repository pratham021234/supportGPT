import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class RuleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"

class ExecutionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    trigger_event = Column(String(100), nullable=False, index=True) # e.g. RAG_QUERY, TICKET_CREATED
    
    # JSONB arrays defining the logic
    # Example condition: [{"field": "confidence", "operator": "lt", "value": 0.6}]
    conditions = Column(JSONB, nullable=False, default=list)
    
    # Example action: [{"type": "CREATE_TICKET", "payload": {"priority": "HIGH"}}]
    actions = Column(JSONB, nullable=False, default=list)
    
    status = Column(Enum(RuleStatus), default=RuleStatus.ACTIVE)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    
    event_id = Column(UUID(as_uuid=True), nullable=True) # ID of the SystemEvent that triggered it
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    error_message = Column(String, nullable=True)
    
    execution_logs = Column(JSONB, nullable=True, default=list)
    
    executed_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    url = Column(String(1000), nullable=False)
    secret = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
