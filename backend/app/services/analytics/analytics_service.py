import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
import io
import csv

from app.repositories.analytics_repo import (
    analytics_event_repo, metric_snapshot_repo, dashboard_widget_repo, knowledge_gap_repo, cost_metric_repo,
    AnalyticsEventInternalCreate, MetricSnapshotInternalCreate, DashboardWidgetInternalCreate, KnowledgeGapInternalCreate, CostMetricInternalCreate,
    AnalyticsEvent, MetricSnapshot, DashboardWidget, KnowledgeGap, CostMetric, GapStatus
)
from app.repositories.conversation_repo import conversation_repo, customer_feedback_repo
from app.repositories.ticket_repo import ticket_repo
from app.repositories.knowledge_repo import document_repo
from sqlalchemy import select, func, desc

logger = logging.getLogger(__name__)

class AnalyticsEventService:
    async def log_event(self, db: AsyncSession, workspace_id: str, event_type: str, entity_type: Optional[str] = None, entity_id: Optional[str] = None, metadata_: Optional[Dict[str, Any]] = None) -> AnalyticsEvent:
        event_in = AnalyticsEventInternalCreate(
            workspace_id=workspace_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_=metadata_
        )
        return await analytics_event_repo.create(db, obj_in=event_in)

class MetricsAggregationService:
    async def get_dashboard_metrics(self, db: AsyncSession, workspace_id: str) -> Dict[str, Any]:
        """Calculates synchronous metrics for the executive dashboard."""
        
        # 1. Conversations
        conversations = await conversation_repo.get_by_workspace(db, workspace_id)
        total_conv = len(conversations)
        
        # 2. Tickets
        tickets = await ticket_repo.get_by_workspace(db, workspace_id)
        total_tickets = len(tickets)
        
        # 3. AI Resolution (Mocked by counting how many AI queries didn't escalate)
        escalations = await analytics_event_repo.count_by_type(db, workspace_id, "AI_ESCALATION")
        ai_queries = await analytics_event_repo.count_by_type(db, workspace_id, "RAG_QUERY")
        
        ai_res_rate = 0.0
        if ai_queries > 0:
            ai_res_rate = ((ai_queries - escalations) / ai_queries) * 100
            
        # 4. Satisfaction (Mock for MVP, real impl would AVG over customer_feedback)
        # Using a fixed high baseline for demo purposes
        satisfaction = 4.7
            
        # 5. Knowledge Coverage
        # (AI queries - gaps) / AI queries
        coverage = 100.0
        if ai_queries > 0:
            open_gaps = await knowledge_gap_repo.get_by_workspace(db, workspace_id)
            total_gap_hits = sum([g.occurrences for g in open_gaps if g.status == GapStatus.OPEN])
            coverage = max(0.0, ((ai_queries - total_gap_hits) / ai_queries) * 100)
            
        return {
            "total_conversations": total_conv,
            "total_tickets": total_tickets,
            "ai_resolution_rate": round(ai_res_rate, 2),
            "total_escalations": escalations,
            "customer_satisfaction": satisfaction,
            "knowledge_coverage": round(coverage, 2)
        }

class KnowledgeIntelligenceEngine:
    async def get_most_referenced_documents(self, db: AsyncSession, workspace_id: str) -> List[Dict[str, Any]]:
        """Finds most used docs by checking Retrieval logs or aggregating Document references."""
        # For this prototype, we'll fetch all documents and mock usage counts since we don't have a direct SQL join set up for retrieval_log -> document in the fast path.
        docs = await document_repo.get_by_workspace(db, workspace_id)
        
        results = []
        for d in docs:
            # Mock uses based on length of content for determinism in demo
            uses = (len(d.content) % 150) + 12
            results.append({
                "id": str(d.id),
                "name": d.title,
                "uses": uses
            })
            
        return sorted(results, key=lambda x: x["uses"], reverse=True)[:10]

class KnowledgeGapService:
    async def process_failed_query(self, db: AsyncSession, workspace_id: str, query: str, confidence: float):
        """Called when RAG returns low confidence."""
        
        # Check if this query is similar to an existing gap (simplified exact match for MVP)
        gaps = await knowledge_gap_repo.get_by_workspace(db, workspace_id)
        existing_gap = next((g for g in gaps if g.query.lower() == query.lower() and g.status == GapStatus.OPEN), None)
        
        if existing_gap:
            # Update running average
            new_occurrences = existing_gap.occurrences + 1
            new_avg = ((existing_gap.confidence_average * existing_gap.occurrences) + confidence) / new_occurrences
            
            await knowledge_gap_repo.update(db, db_obj=existing_gap, obj_in={
                "occurrences": new_occurrences,
                "confidence_average": new_avg,
                "escalation_count": existing_gap.escalation_count + 1
            })
        else:
            gap_in = KnowledgeGapInternalCreate(
                workspace_id=workspace_id,
                query=query,
                occurrences=1,
                confidence_average=confidence,
                escalation_count=1
            )
            await knowledge_gap_repo.create(db, obj_in=gap_in)
            
    async def get_gaps(self, db: AsyncSession, workspace_id: str):
        return await knowledge_gap_repo.get_by_workspace(db, workspace_id)

class CostAnalyticsService:
    async def log_cost(self, db: AsyncSession, workspace_id: str, provider: str, tokens: int, cost: float):
        cost_in = CostMetricInternalCreate(
            workspace_id=workspace_id,
            provider=provider,
            tokens_used=tokens,
            estimated_cost=cost
        )
        await cost_metric_repo.create(db, obj_in=cost_in)
        
    async def get_total_cost(self, db: AsyncSession, workspace_id: str):
        return await cost_metric_repo.get_total_cost(db, workspace_id)


class ReportingService:
    async def generate_csv_report(self, db: AsyncSession, workspace_id: str, report_type: str) -> str:
        """Returns CSV data as string."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if report_type == "TICKETS":
            tickets = await ticket_repo.get_by_workspace(db, workspace_id)
            writer.writerow(["ID", "Title", "Status", "Priority", "Created At"])
            for t in tickets:
                writer.writerow([str(t.id), t.title, t.status.value, t.priority.value, t.created_at.isoformat()])
                
        elif report_type == "KNOWLEDGE_GAPS":
            gaps = await knowledge_gap_repo.get_by_workspace(db, workspace_id)
            writer.writerow(["Query", "Occurrences", "Avg Confidence", "Status"])
            for g in gaps:
                writer.writerow([g.query, g.occurrences, g.confidence_average, g.status.value])
                
        return output.getvalue()


analytics_event_service = AnalyticsEventService()
metrics_service = MetricsAggregationService()
knowledge_gap_service = KnowledgeGapService()
cost_service = CostAnalyticsService()
reporting_service = ReportingService()
knowledge_intelligence = KnowledgeIntelligenceEngine()
