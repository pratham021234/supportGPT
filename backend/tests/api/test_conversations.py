import pytest
from httpx import AsyncClient
from typing import Dict, Any

pytestmark = pytest.mark.asyncio

async def test_create_customer(client: AsyncClient, test_workspace: Dict[str, Any]):
    response = await client.post(
        "/api/v1/conversations/customers",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert "id" in data

async def test_create_conversation(client: AsyncClient, test_workspace: Dict[str, Any]):
    # First create a customer
    cust_res = await client.post(
        "/api/v1/conversations/customers",
        json={"name": "John Smith", "email": "john@example.com"}
    )
    customer_id = cust_res.json()["id"]

    # Now create conversation
    response = await client.post(
        "/api/v1/conversations",
        json={
            "customer_id": customer_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["status"] == "OPEN"
    assert "id" in data

async def test_add_manual_message_and_internal_note(client: AsyncClient):
    # Setup customer and conversation
    cust_res = await client.post("/api/v1/conversations/customers", json={"name": "Test", "email": "test@test.com"})
    customer_id = cust_res.json()["id"]
    conv_res = await client.post("/api/v1/conversations", json={"customer_id": customer_id})
    conv_id = conv_res.json()["id"]

    # 1. Add normal agent message
    msg_res = await client.post(
        f"/api/v1/conversations/{conv_id}/message",
        json={
            "content": "Hello how can I help?",
            "is_internal": False
        }
    )
    assert msg_res.status_code == 200
    msg_data = msg_res.json()
    assert msg_data["content"] == "Hello how can I help?"
    assert msg_data["sender_type"] == "AGENT"
    assert msg_data["is_internal"] is False

    # 2. Add internal note
    note_res = await client.post(
        f"/api/v1/conversations/{conv_id}/message",
        json={
            "content": "Customer is angry",
            "is_internal": True
        }
    )
    assert note_res.status_code == 200
    note_data = note_res.json()
    assert note_data["content"] == "Customer is angry"
    assert note_data["sender_type"] == "SYSTEM"
    assert note_data["is_internal"] is True

async def test_escalate_and_resolve_conversation(client: AsyncClient):
    cust_res = await client.post("/api/v1/conversations/customers", json={"name": "Test", "email": "test@test.com"})
    conv_res = await client.post("/api/v1/conversations", json={"customer_id": cust_res.json()["id"]})
    conv_id = conv_res.json()["id"]

    # Escalate
    esc_res = await client.post(
        f"/api/v1/conversations/{conv_id}/escalate",
        json={"reason": "Customer requested human"}
    )
    assert esc_res.status_code == 200
    
    # Check status is HANDOFF or WAITING (depending on exact handoff_service trigger config)
    get_res = await client.get(f"/api/v1/conversations/{conv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] in ["WAITING", "HANDOFF", "ACTIVE"]

    # Resolve
    res_res = await client.post(f"/api/v1/conversations/{conv_id}/resolve")
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"

async def test_conversation_analytics(client: AsyncClient):
    # Just verify endpoint returns 200 and shape is correct
    response = await client.get("/api/v1/conversations/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversations" in data
    assert "resolved_conversations" in data
    assert "escalations" in data
    assert "ai_resolution_rate" in data

async def test_search_conversations(client: AsyncClient):
    response = await client.get("/api/v1/conversations/search?query=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
