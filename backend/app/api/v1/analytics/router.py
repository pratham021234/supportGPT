from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.analytics.analytics_service import (
    analytics_event_service, metrics_service, knowledge_gap_service, cost_service, reporting_service, knowledge_intelligence
)
from app.services.analytics.insights_engine import insights_engine
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

class EventCreateRequest(BaseModel):
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    metadata_: Optional[dict] = None

class ReportExportRequest(BaseModel):
    report_type: str # "TICKETS" or "KNOWLEDGE_GAPS"
    format: str = "CSV"

@router.post("/events")
async def log_event(
    req: EventCreateRequest,
    member: WorkspaceMember = Depends(require_permission("view_analytics")), # typically this is internal, but mocked for MVP
    db: AsyncSession = Depends(get_db)
):
    event = await analytics_event_service.log_event(
        db, str(member.workspace_id), req.event_type, req.entity_type, req.entity_id, req.metadata_
    )
    return {"message": "Event logged", "id": str(event.id)}

@router.get("/dashboard")
async def get_dashboard(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    metrics = await metrics_service.get_dashboard_metrics(db, str(member.workspace_id), time_range)
    return metrics

@router.get("/overview")
async def get_overview(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await get_dashboard(time_range, member, db)

@router.get("/volume")
async def get_volume(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await metrics_service.get_volume_metrics(db, str(member.workspace_id), time_range)

@router.get("/conversations")
async def get_conversations(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await get_volume(time_range, member, db)

@router.get("/resolution")
async def get_resolution(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await metrics_service.get_resolution_metrics(db, str(member.workspace_id), time_range)

@router.get("/escalations")
async def get_escalations(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await metrics_service.get_escalation_metrics(db, str(member.workspace_id), time_range)

@router.get("/tickets")
async def get_tickets(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await get_escalations(time_range, member, db)

@router.get("/system-status")
async def get_system_status(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
):
    return await metrics_service.get_system_status()
    
@router.get("/agents/summary")
async def get_agents_summary(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await metrics_service.get_agent_summary(db, str(member.workspace_id))

@router.get("/agents")
async def get_agents(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await get_agents_summary(member, db)

@router.get("/top-questions")
async def get_top_questions(
    time_range: Optional[str] = "7d",
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_intelligence.get_top_questions(db, str(member.workspace_id), time_range)

@router.get("/confidence-alerts")
async def get_confidence_alerts(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_intelligence.get_confidence_alerts(db, str(member.workspace_id))

@router.get("/knowledge-gaps")
async def get_knowledge_gaps(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_gap_service.get_gaps(db, str(member.workspace_id))

@router.get("/knowledge/most-referenced")
async def get_most_referenced_documents(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_intelligence.get_most_referenced_documents(db, str(member.workspace_id))

@router.get("/knowledge")
async def get_knowledge(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    gaps = await knowledge_gap_service.get_gaps(db, str(member.workspace_id))
    most_ref = await knowledge_intelligence.get_most_referenced_documents(db, str(member.workspace_id))
    return {
        "most_referenced": most_ref,
        "gaps": gaps
    }

@router.get("/insights")
async def get_business_insights(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    return await insights_engine.generate_knowledge_recommendations(db, str(member.workspace_id))

@router.get("/costs")
async def get_costs(
    member: WorkspaceMember = Depends(require_permission("view_costs")),
    db: AsyncSession = Depends(get_db)
):
    total = await cost_service.get_total_cost(db, str(member.workspace_id))
    return {"total_estimated_cost_usd": total}

@router.get("/workspace")
async def get_workspace(
    member: WorkspaceMember = Depends(require_permission("view_analytics")),
    db: AsyncSession = Depends(get_db)
):
    system = await metrics_service.get_system_status()
    total = await cost_service.get_total_cost(db, str(member.workspace_id))
    return {
        "status": system,
        "total_estimated_cost_usd": total
    }

@router.post("/reports/export")
async def export_report(
    req: ReportExportRequest,
    member: WorkspaceMember = Depends(require_permission("export_reports")),
    db: AsyncSession = Depends(get_db)
):
    if req.format.upper() != "CSV":
        raise HTTPException(status_code=400, detail="Only CSV is supported currently")
        
    csv_data = await reporting_service.generate_csv_report(db, str(member.workspace_id), req.report_type.upper())
    
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={req.report_type.lower()}_export.csv"}
    )

@router.post("/reports")
async def generate_report(
    req: ReportExportRequest,
    member: WorkspaceMember = Depends(require_permission("export_reports")),
    db: AsyncSession = Depends(get_db)
):
    return await export_report(req, member, db)

# Active realtime dashboard connections
_realtime_connections = {}

@router.websocket("/realtime")
async def realtime_dashboard(websocket: WebSocket):
    # Standard WS token auth applies here (simplified for MVP)
    await websocket.accept()
    # Read workspace_id from query params or auth context. For MVP, we'll fake it.
    workspace_id = "default"
    if workspace_id not in _realtime_connections:
        _realtime_connections[workspace_id] = []
    _realtime_connections[workspace_id].append(websocket)
    
    try:
        while True:
            # Keepalive or simulated live stream
            data = await websocket.receive_text()
            # In a real impl, we would listen to a Redis pub/sub for live events across all servers.
            # Here we just respond to ping or loop.
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        _realtime_connections[workspace_id].remove(websocket)
        
async def broadcast_realtime_event(workspace_id: str, event_type: str, data: dict):
    if workspace_id in _realtime_connections:
        for ws in _realtime_connections[workspace_id]:
            try:
                await ws.send_json({"event_type": event_type, "data": data})
            except:
                pass
