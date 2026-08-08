from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.repositories.base import BaseRepository
from app.models.rag import QueryLog, AnswerLog, RetrievalLog, CitationLog, EscalationEvent, EscalationStatus
from pydantic import BaseModel

class QueryLogInternalCreate(BaseModel):
    workspace_id: str
    user_id: Optional[str] = None
    query: str
    language: Optional[str] = None
    query_type: Optional[str] = None
    input_tokens: int = 0
    latency_ms: int = 0

class AnswerLogInternalCreate(BaseModel):
    query_id: str
    workspace_id: str
    answer_text: str
    confidence_score: float
    output_tokens: int = 0

class RetrievalLogInternalCreate(BaseModel):
    query_id: str
    chunk_id: Optional[str] = None
    similarity_score: float

class CitationLogInternalCreate(BaseModel):
    answer_id: str
    chunk_id: Optional[str] = None
    claim_text: Optional[str] = None

class EscalationEventInternalCreate(BaseModel):
    workspace_id: str
    query_id: str
    confidence_score: float
    threshold: float = 70.0
    status: EscalationStatus = EscalationStatus.PENDING

class QueryLogRepository(BaseRepository[QueryLog, QueryLogInternalCreate, BaseModel]):
    pass

class AnswerLogRepository(BaseRepository[AnswerLog, AnswerLogInternalCreate, BaseModel]):
    pass

class RetrievalLogRepository(BaseRepository[RetrievalLog, RetrievalLogInternalCreate, BaseModel]):
    pass

class CitationLogRepository(BaseRepository[CitationLog, CitationLogInternalCreate, BaseModel]):
    pass

class EscalationEventRepository(BaseRepository[EscalationEvent, EscalationEventInternalCreate, BaseModel]):
    pass

query_log_repo = QueryLogRepository(QueryLog)
answer_log_repo = AnswerLogRepository(AnswerLog)
retrieval_log_repo = RetrievalLogRepository(RetrievalLog)
citation_log_repo = CitationLogRepository(CitationLog)
escalation_event_repo = EscalationEventRepository(EscalationEvent)
