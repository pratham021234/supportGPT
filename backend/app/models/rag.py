import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class EscalationStatus(str, enum.Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

class QueryLog(Base):
    __tablename__ = "rag_query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    query = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)
    query_type = Column(String(50), nullable=True) # e.g. FAQ, TECHNICAL, PROCEDURAL
    
    input_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    workspace = relationship("Workspace")
    user = relationship("User")

class AnswerLog(Base):
    __tablename__ = "rag_answer_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    query_id = Column(UUID(as_uuid=True), ForeignKey("rag_query_logs.id", ondelete="CASCADE"), nullable=False, unique=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    answer_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False) # 0.0 to 100.0
    
    output_tokens = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    query_log = relationship("QueryLog")
    workspace = relationship("Workspace")

class RetrievalLog(Base):
    __tablename__ = "rag_retrieval_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    query_id = Column(UUID(as_uuid=True), ForeignKey("rag_query_logs.id", ondelete="CASCADE"), nullable=False)
    
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    similarity_score = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    query_log = relationship("QueryLog")
    chunk = relationship("DocumentChunk")

class CitationLog(Base):
    __tablename__ = "rag_citation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("rag_answer_logs.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    
    claim_text = Column(Text, nullable=True) # the specific text supported by this citation
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    answer = relationship("AnswerLog")
    chunk = relationship("DocumentChunk")

class EscalationEvent(Base):
    __tablename__ = "rag_escalation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    query_id = Column(UUID(as_uuid=True), ForeignKey("rag_query_logs.id", ondelete="CASCADE"), nullable=False)
    
    confidence_score = Column(Float, nullable=False)
    threshold = Column(Float, default=70.0)
    
    status = Column(Enum(EscalationStatus), default=EscalationStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    workspace = relationship("Workspace")
    query_log = relationship("QueryLog")
