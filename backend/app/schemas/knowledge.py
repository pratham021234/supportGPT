from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl

from app.models.knowledge import SourceType, DocumentStatus

# --- Tags ---
class KnowledgeTagBase(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeTagCreate(KnowledgeTagBase):
    pass

class KnowledgeTagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class KnowledgeTagResponse(KnowledgeTagBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# --- Sources ---
class KnowledgeSourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: SourceType

class KnowledgeSourceCreate(KnowledgeSourceBase):
    pass

class KnowledgeSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class KnowledgeSourceResponse(KnowledgeSourceBase):
    id: UUID
    workspace_id: UUID
    status: DocumentStatus
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Documents ---
class DocumentBase(BaseModel):
    title: str
    language: Optional[str] = "en"

class DocumentCreate(DocumentBase):
    source_id: Optional[UUID] = None
    # For file uploads, title is provided as form data usually
    # This schema is mainly used internally for the DB representation

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: UUID
    workspace_id: UUID
    source_id: Optional[UUID] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    status: DocumentStatus
    version: int
    is_current_version: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    tags: List[KnowledgeTagResponse] = []

    class Config:
        from_attributes = True

# --- FAQs ---
class FAQBase(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

class FAQCreate(FAQBase):
    pass

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None

class FAQResponse(FAQBase):
    id: UUID
    workspace_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Search & Analytics ---
class SearchQuery(BaseModel):
    query: str
    source_type: Optional[SourceType] = None
    status: Optional[DocumentStatus] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20
    offset: int = 0

class SearchResultItem(BaseModel):
    id: UUID
    type: str # "document" or "faq"
    title: str # document title or faq question
    preview: str # chunk content or faq answer
    score: Optional[float] = None # For future vector search
    metadata_: Optional[Any] = None

class SearchResponse(BaseModel):
    items: List[SearchResultItem]
    total: int

class KnowledgeHealthResponse(BaseModel):
    total_documents: int
    total_faqs: int
    processing_documents: int
    failed_documents: int
    active_sources: int
    total_storage_bytes: int
