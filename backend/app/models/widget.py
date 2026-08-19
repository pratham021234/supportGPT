import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class WidgetConfiguration(Base):
    __tablename__ = "widget_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True) # Optional: generic fallback if null
    
    theme = Column(String(50), default="light")
    primary_color = Column(String(20), default="#000000")
    logo_url = Column(String(255), nullable=True)
    launcher_text = Column(String(100), default="Chat with us")
    welcome_message = Column(Text, default="Hello! How can I help you today?")
    position = Column(String(50), default="bottom-right")
    border_radius = Column(String(20), default="8px")
    
    allowed_domains = Column(JSONB, default=list, nullable=True)
    suggested_questions = Column(JSONB, default=list, nullable=True)
    offline_message = Column(Text, default="We are currently offline. Please leave a message or create a ticket.")
    support_hours = Column(JSONB, default=dict, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class WidgetSession(Base):
    """Tracks anonymous or public customer sessions initialized via the widget."""
    __tablename__ = "widget_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_activity_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
