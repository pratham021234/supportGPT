import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class AgentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DISABLED = "DISABLED"

class AgentType(str, enum.Enum):
    SUPPORT = "SUPPORT"
    SALES = "SALES"
    TECHNICAL = "TECHNICAL"
    HR = "HR"
    OPERATIONS = "OPERATIONS"
    CUSTOM = "CUSTOM"

class AgentVisibility(str, enum.Enum):
    PRIVATE = "PRIVATE"
    INTERNAL = "INTERNAL"
    PUBLIC = "PUBLIC"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    status = Column(Enum(AgentStatus), default=AgentStatus.DRAFT, nullable=False)
    agent_type = Column(Enum(AgentType), default=AgentType.CUSTOM, nullable=False)
    visibility = Column(Enum(AgentVisibility), default=AgentVisibility.INTERNAL, nullable=False)
    
    default_language = Column(String(10), default="en")
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace")
    creator = relationship("User")
    
    prompt = relationship("AgentPrompt", uselist=False, back_populates="agent", cascade="all, delete-orphan")
    model_config = relationship("AgentModelConfig", uselist=False, back_populates="agent", cascade="all, delete-orphan")
    escalation_rule = relationship("AgentEscalationRule", uselist=False, back_populates="agent", cascade="all, delete-orphan")
    knowledge_scopes = relationship("AgentKnowledgeScope", back_populates="agent", cascade="all, delete-orphan")
    versions = relationship("AgentVersion", back_populates="agent", cascade="all, delete-orphan")

class AgentPrompt(Base):
    __tablename__ = "agent_prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    system_prompt = Column(Text, nullable=False, default="You are a helpful support agent. Answer questions using the provided context.")
    welcome_message = Column(Text, nullable=True, default="Hello! How can I help you today?")
    fallback_message = Column(Text, nullable=True, default="I couldn't find reliable information. Would you like to speak with a human agent?")
    tone = Column(String(50), default="Professional")
    behavior_rules = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="prompt")

class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    
    version_number = Column(Integer, nullable=False)
    configuration_snapshot = Column(JSONB, nullable=False)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="versions")

class AgentKnowledgeScope(Base):
    __tablename__ = "agent_knowledge_scopes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    
    # Scoping rules
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_tags.id", ondelete="CASCADE"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="knowledge_scopes")

class AgentModelConfig(Base):
    __tablename__ = "agent_model_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    provider = Column(String(50), default="google")
    model = Column(String(100), default="gemini-2.5-flash")
    
    temperature = Column(Float, default=0.2)
    max_tokens = Column(Integer, default=2048)
    top_p = Column(Float, default=0.95)
    frequency_penalty = Column(Float, default=0.0)
    presence_penalty = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="model_config")

class AgentEscalationRule(Base):
    __tablename__ = "agent_escalation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    confidence_threshold = Column(Float, default=70.0)
    auto_create_ticket = Column(Boolean, default=False)
    auto_handoff = Column(Boolean, default=True)
    escalation_message = Column(Text, nullable=True, default="Let me connect you with a human agent who can help.")
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="escalation_rule")
