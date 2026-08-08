from typing import List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, desc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.knowledge import (
    KnowledgeSource, Document, DocumentPage, DocumentChunk, FAQ, KnowledgeTag, DocumentTag, DocumentStatus
)
from pydantic import BaseModel

# Internal Create Schemas
class KnowledgeSourceInternalCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    source_type: str
    created_by: Optional[str] = None

class DocumentInternalCreate(BaseModel):
    workspace_id: str
    source_id: Optional[str] = None
    title: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_path: Optional[str] = None
    language: Optional[str] = "en"
    created_by: Optional[str] = None
    previous_version_id: Optional[str] = None
    version: int = 1

class FAQInternalCreate(BaseModel):
    workspace_id: str
    question: str
    answer: str
    category: Optional[str] = None
    created_by: Optional[str] = None

class KnowledgeTagInternalCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None

# Repositories
class KnowledgeSourceRepository(BaseRepository[KnowledgeSource, KnowledgeSourceInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[KnowledgeSource]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

class DocumentRepository(BaseRepository[Document, DocumentInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id,
            self.model.is_current_version == True
        ).options(selectinload(self.model.tags)).order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_with_tags(self, db: AsyncSession, id: str) -> Optional[Document]:
        query = select(self.model).where(self.model.id == id).options(selectinload(self.model.tags))
        result = await db.execute(query)
        return result.scalars().first()

class FAQRepository(BaseRepository[FAQ, FAQInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[FAQ]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

class KnowledgeTagRepository(BaseRepository[KnowledgeTag, KnowledgeTagInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[KnowledgeTag]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_name(self, db: AsyncSession, workspace_id: str, name: str) -> Optional[KnowledgeTag]:
        query = select(self.model).where(self.model.workspace_id == workspace_id, self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first()

# Instances
knowledge_source_repo = KnowledgeSourceRepository(KnowledgeSource)
document_repo = DocumentRepository(Document)
faq_repo = FAQRepository(FAQ)
knowledge_tag_repo = KnowledgeTagRepository(KnowledgeTag)
