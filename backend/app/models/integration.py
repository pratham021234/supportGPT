import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum

class ConnectionStatus(str, enum.Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"

class SyncStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class IntegrationConnection(Base):
    __tablename__ = "integration_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    provider = Column(String(50), nullable=False) # e.g. "slack", "hubspot", "salesforce"
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.CONNECTED)
    
    # Store OAuth tokens/secrets encrypted in production, plaintext for MVP
    access_token = Column(String(2000), nullable=True)
    refresh_token = Column(String(2000), nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional configuration (e.g. default channel for slack)
    config = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("integration_connections.id", ondelete="CASCADE"), nullable=False)
    
    provider = Column(String(50), nullable=False)
    resource_type = Column(String(100), nullable=False) # e.g. "ticket", "contact"
    resource_id = Column(String(100), nullable=False) 
    
    action = Column(String(50), nullable=False) # e.g. "CREATE", "UPDATE", "DELETE"
    status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    
    error_message = Column(String(2000), nullable=True)
    payload_snapshot = Column(JSONB, nullable=True)
    
    retry_count = Column(int, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
