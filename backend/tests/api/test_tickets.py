import pytest
from httpx import AsyncClient
from typing import Dict, Any

pytestmark = pytest.mark.asyncio

async def test_create_ticket(client: AsyncClient, test_workspace: Dict[str, Any]):
    response = await client.post(
        "/api/v1/tickets",
        json={
            "title": "Need help with billing",
            "description": "I was overcharged by $10",
            "priority": "HIGH"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Need help with billing"
    assert data["status"] == "OPEN"
    assert "ticket_number" in data
    assert "TCK-" in data["ticket_number"]

async def test_assign_ticket(client: AsyncClient, test_workspace: Dict[str, Any]):
    # Create ticket
    t_res = await client.post(
        "/api/v1/tickets",
        json={"title": "Test assign", "priority": "MEDIUM"}
    )
    ticket_id = t_res.json()["id"]

    # Assign manually
    # Note: test_workspace has a user, but we'll just mock user ID for now
    user_id = test_workspace["user_id"]
    assign_res = await client.post(
        f"/api/v1/tickets/{ticket_id}/assign",
        json={"assigned_user_id": user_id, "strategy": "MANUAL"}
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_to"] == user_id

async def test_escalate_ticket(client: AsyncClient, test_workspace: Dict[str, Any]):
    # Create ticket
    t_res = await client.post(
        "/api/v1/tickets",
        json={"title": "Test escalate", "priority": "MEDIUM"}
    )
    ticket_id = t_res.json()["id"]

    # Escalate
    esc_res = await client.post(
        f"/api/v1/tickets/{ticket_id}/escalate",
        json={"reason": "Customer is angry"}
    )
    assert esc_res.status_code == 200
    data = esc_res.json()
    assert data["status"] == "ESCALATED"
    # Medium goes to High on escalate
    assert data["priority"] == "HIGH"

async def test_ticket_comments(client: AsyncClient, test_workspace: Dict[str, Any]):
    t_res = await client.post(
        "/api/v1/tickets",
        json={"title": "Test comments", "priority": "LOW"}
    )
    ticket_id = t_res.json()["id"]

    c_res = await client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        json={"content": "Checking on this", "is_internal": True}
    )
    assert c_res.status_code == 200
    assert c_res.json()["is_internal"] is True
    
    get_res = await client.get(f"/api/v1/tickets/{ticket_id}/comments")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1

async def test_ticket_search(client: AsyncClient, test_workspace: Dict[str, Any]):
    t_res = await client.post(
        "/api/v1/tickets",
        json={"title": "FindMeTicket", "priority": "LOW"}
    )
    
    search_res = await client.get("/api/v1/tickets/search?query=FindMeTicket")
    assert search_res.status_code == 200
    data = search_res.json()
    assert len(data) >= 1
    assert any(t["title"] == "FindMeTicket" for t in data)

async def test_ticket_analytics(client: AsyncClient, test_workspace: Dict[str, Any]):
    res = await client.get("/api/v1/tickets/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "analytics" in data
    assert "knowledge_gaps" in data
    assert "total_tickets" in data["analytics"]
    assert "top_ticket_drivers" in data["knowledge_gaps"]
