import pytest
from httpx import AsyncClient
from typing import Dict, Any

pytestmark = pytest.mark.asyncio

async def test_get_analytics_overview(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.get(
        "/api/v1/analytics/overview?time_range=7d",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "total_conversations" in data
    assert "ai_resolution_rate" in data

async def test_get_ticket_analytics(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.get(
        "/api/v1/analytics/tickets?time_range=30d",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "created" in data
    assert "resolved" in data

async def test_get_ai_performance(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.get(
        "/api/v1/analytics/ai-performance?time_range=today",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "avg_confidence" in data
    assert "hallucination_risk" in data

async def test_get_csat(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.get(
        "/api/v1/analytics/csat?time_range=7d",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "csat_score" in data

async def test_export_reports(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.post(
        "/api/v1/analytics/reports/export",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"report_type": "TICKETS", "format": "CSV"}
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/csv; charset=utf-8"
