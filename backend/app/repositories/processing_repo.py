from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.repositories.base import BaseRepository
from app.models.processing import ProcessingJob, ExtractionResult, JobStatus, JobType
from pydantic import BaseModel

# Internal Create Schemas
class ProcessingJobInternalCreate(BaseModel):
    workspace_id: str
    document_id: Optional[str] = None
    job_type: JobType = JobType.DOCUMENT_PROCESSING
    status: JobStatus = JobStatus.QUEUED

class ExtractionResultInternalCreate(BaseModel):
    document_id: str
    raw_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    detected_language: Optional[str] = None
    page_count: int = 0
    character_count: int = 0
    word_count: int = 0
    metadata_: dict = {}

# Repositories
class ProcessingJobRepository(BaseRepository[ProcessingJob, ProcessingJobInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[ProcessingJob]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_document(self, db: AsyncSession, document_id: str) -> Optional[ProcessingJob]:
        query = select(self.model).where(self.model.document_id == document_id).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return result.scalars().first()

class ExtractionResultRepository(BaseRepository[ExtractionResult, ExtractionResultInternalCreate, BaseModel]):
    async def get_by_document(self, db: AsyncSession, document_id: str) -> Optional[ExtractionResult]:
        query = select(self.model).where(self.model.document_id == document_id)
        result = await db.execute(query)
        return result.scalars().first()

# Instances
processing_job_repo = ProcessingJobRepository(ProcessingJob)
extraction_result_repo = ExtractionResultRepository(ExtractionResult)
