from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.repositories.base import BaseRepository
from app.models.vector import EmbeddingJob, VectorCollection, SearchEvent, EmbeddingJobStatus
from pydantic import BaseModel

# Internal Create Schemas
class EmbeddingJobInternalCreate(BaseModel):
    workspace_id: str
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    provider: str
    status: EmbeddingJobStatus = EmbeddingJobStatus.PENDING

class VectorCollectionInternalCreate(BaseModel):
    workspace_id: str
    name: str
    provider: str
    embedding_dimension: int

class SearchEventInternalCreate(BaseModel):
    workspace_id: str
    user_id: Optional[str] = None
    query: str
    search_type: str
    results_count: int = 0
    latency_ms: Optional[int] = None

# Repositories
class EmbeddingJobRepository(BaseRepository[EmbeddingJob, EmbeddingJobInternalCreate, BaseModel]):
    async def get_by_document(self, db: AsyncSession, document_id: str) -> List[EmbeddingJob]:
        query = select(self.model).where(self.model.document_id == document_id)
        result = await db.execute(query)
        return list(result.scalars().all())

class VectorCollectionRepository(BaseRepository[VectorCollection, VectorCollectionInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> Optional[VectorCollection]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return result.scalars().first()

class SearchEventRepository(BaseRepository[SearchEvent, SearchEventInternalCreate, BaseModel]):
    pass

# Instances
embedding_job_repo = EmbeddingJobRepository(EmbeddingJob)
vector_collection_repo = VectorCollectionRepository(VectorCollection)
search_event_repo = SearchEventRepository(SearchEvent)
