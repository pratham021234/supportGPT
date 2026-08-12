import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin
import enum

class SourceType(str, enum.Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    TXT = "TXT"
    MARKDOWN = "MARKDOWN"
    WEBSITE = "WEBSITE"
    FAQ = "FAQ"
    ARTICLE = "ARTICLE"

class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class KnowledgeSource(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "knowledge_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(SourceType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    workspace = relationship("Workspace")
    creator = relationship("User", foreign_keys="[KnowledgeSource.created_by]")
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")

class Document(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    file_name = Column(String(500), nullable=True)
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    storage_path = Column(Text, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    processing_status = Column(String(50), default="PENDING", nullable=True)
    language = Column(String(10), default="en")
    version = Column(Integer, default=1)
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    checksum = Column(String(255), nullable=True, index=True)
    last_processed_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    original_filename = Column(String(500), nullable=True)
    
    # Track versioning (self-referential)
    previous_version_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    is_current_version = Column(Boolean, default=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace")
    source = relationship("KnowledgeSource", back_populates="documents")
    creator = relationship("User", foreign_keys="[Document.created_by]")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    activities = relationship("DocumentActivity", back_populates="document", cascade="all, delete-orphan")
    
    # Document tags mapping
    tags = relationship("KnowledgeTag", secondary="document_tags", back_populates="documents")

class DocumentPage(Base, TimestampMixin):
    __tablename__ = "document_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)  # Using metadata_ since metadata is reserved in SQLAlchemy Base

    document = relationship("Document", back_populates="pages")
    chunks = relationship("DocumentChunk", back_populates="page")

class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    chunk_type = Column(String(50), nullable=True) # e.g. TEXT, TABLE, HEADER
    metadata_ = Column("metadata", JSONB, nullable=True)

    workspace = relationship("Workspace")

    document = relationship("Document", back_populates="chunks")
    page = relationship("DocumentPage", back_populates="chunks")

class FAQ(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(255), nullable=True)

    workspace = relationship("Workspace")
    creator = relationship("User", foreign_keys="[FAQ.created_by]")

class KnowledgeTag(Base, TimestampMixin):
    __tablename__ = "knowledge_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    workspace = relationship("Workspace")
    documents = relationship("Document", secondary="document_tags", back_populates="tags")

class DocumentTag(Base):
    __tablename__ = "document_tags"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_tags.id", ondelete="CASCADE"), primary_key=True)

class DocumentVersion(Base, TimestampMixin, AuditMixin):
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    version_number = Column(Integer, nullable=False)
    storage_path = Column(Text, nullable=True)
    checksum = Column(String(255), nullable=True, index=True)
    file_size = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    document = relationship("Document", back_populates="versions")
    workspace = relationship("Workspace")

class DocumentActivity(Base, TimestampMixin):
    __tablename__ = "document_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    activity_type = Column(String(50), nullable=False) # e.g. UPLOAD, EDIT, DELETE, RESTORE, REPROCESS, VERSION_UPLOAD
    details = Column(JSONB, nullable=True)

    document = relationship("Document", back_populates="activities")
    workspace = relationship("Workspace")
    user = relationship("User")
