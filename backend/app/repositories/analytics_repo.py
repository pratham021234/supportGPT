from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func

from app.repositories.base import BaseRepository
from app.models.analytics import (
    AnalyticsEvent, MetricSnapshot, DashboardWidget, KnowledgeGap, CostMetric, GapStatus
)
from pydantic import BaseModel

class AnalyticsEventInternalCreate(BaseModel):
    workspace_id: str
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None

class MetricSnapshotInternalCreate(BaseModel):
    workspace_id: str
    metric_name: str
    metric_value: float
    aggregation_period: str
    snapshot_date: Any # datetime

class DashboardWidgetInternalCreate(BaseModel):
    workspace_id: str
    widget_type: str
    configuration: Dict[str, Any]
    position: int = 0

class KnowledgeGapInternalCreate(BaseModel):
    workspace_id: str
    query: str
    occurrences: int = 1
    confidence_average: float = 0.0
    escalation_count: int = 0
    status: GapStatus = GapStatus.OPEN

class CostMetricInternalCreate(BaseModel):
    workspace_id: str
    provider: str
    tokens_used: int
    estimated_cost: float

class AnalyticsEventRepository(BaseRepository[AnalyticsEvent, AnalyticsEventInternalCreate, BaseModel]):
    async def get_by_workspace_and_type(self, db: AsyncSession, workspace_id: str, event_type: str) -> List[AnalyticsEvent]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id,
            self.model.event_type == event_type
        ).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_by_type(self, db: AsyncSession, workspace_id: str, event_type: str) -> int:
        query = select(func.count(self.model.id)).where(
            self.model.workspace_id == workspace_id,
            self.model.event_type == event_type
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() or 0

class MetricSnapshotRepository(BaseRepository[MetricSnapshot, MetricSnapshotInternalCreate, BaseModel]):
    pass

class DashboardWidgetRepository(BaseRepository[DashboardWidget, DashboardWidgetInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[DashboardWidget]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id
        ).order_by(self.model.position)
        result = await db.execute(query)
        return list(result.scalars().all())

class KnowledgeGapRepository(BaseRepository[KnowledgeGap, KnowledgeGapInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[KnowledgeGap]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id
        ).order_by(desc(self.model.occurrences))
        result = await db.execute(query)
        return list(result.scalars().all())

class CostMetricRepository(BaseRepository[CostMetric, CostMetricInternalCreate, BaseModel]):
    async def get_total_cost(self, db: AsyncSession, workspace_id: str) -> float:
        query = select(func.sum(self.model.estimated_cost)).where(
            self.model.workspace_id == workspace_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() or 0.0

analytics_event_repo = AnalyticsEventRepository(AnalyticsEvent)
metric_snapshot_repo = MetricSnapshotRepository(MetricSnapshot)
dashboard_widget_repo = DashboardWidgetRepository(DashboardWidget)
knowledge_gap_repo = KnowledgeGapRepository(KnowledgeGap)
cost_metric_repo = CostMetricRepository(CostMetric)
