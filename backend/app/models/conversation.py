import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin
import enum

class ConversationStatus(str, enum.Enum):
    OPEN = "OPEN"
    ACTIVE = "ACTIVE"
    WAITING = "WAITING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class ConversationChannel(str, enum.Enum):
    WEB_CHAT = "WEB_CHAT"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SLACK = "SLACK"
    API = "API"

class SenderType(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    AI_AGENT = "AI_AGENT"
    SUPPORT_AGENT = "SUPPORT_AGENT"
    SYSTEM = "SYSTEM"

class MessageType(str, enum.Enum):
    TEXT = "TEXT"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    ESCALATION = "ESCALATION"
    CITATION = "CITATION"
    ATTACHMENT = "ATTACHMENT"

class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    external_id = Column(String(255), nullable=True, index=True)
    
    metadata_ = Column("metadata", JSONB, nullable=True)
    
    first_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    workspace = relationship("Workspace")
    conversations = relationship("Conversation", back_populates="customer", cascade="all, delete-orphan")

class Conversation(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    status = Column(Enum(ConversationStatus), default=ConversationStatus.OPEN, nullable=False)
    channel = Column(Enum(ConversationChannel), default=ConversationChannel.WEB_CHAT, nullable=False)
    
    is_human_active = Column(Boolean, default=False)
    
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_message_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    workspace = relationship("Workspace")
    customer = relationship("Customer", back_populates="conversations")
    agent = relationship("Agent")
    assigned_user = relationship("User", foreign_keys="[Conversation.assigned_user_id]")
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    events = relationship("ConversationEvent", back_populates="conversation", cascade="all, delete-orphan")
    assignments = relationship("ConversationAssignment", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sender_type = Column(Enum(SenderType), nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=True) # Could be Customer ID, Agent ID, or User ID
    
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    
    metadata_ = Column("metadata", JSONB, nullable=True)
    
    conversation = relationship("Conversation", back_populates="messages")

class ConversationAssignment(Base, TimestampMixin):
    __tablename__ = "conversation_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="assignments")

class ConversationEvent(Base, TimestampMixin):
    __tablename__ = "conversation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    event_type = Column(String(50), nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    
    conversation = relationship("Conversation", back_populates="events")

class CustomerFeedback(Base, TimestampMixin):
    __tablename__ = "customer_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    is_helpful = Column(Boolean, nullable=True)
    rating = Column(Integer, nullable=True)  # 1 to 5
    comment = Column(Text, nullable=True)
    
    conversation = relationship("Conversation", backref="feedback")
