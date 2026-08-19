import pytest
from httpx import AsyncClient
from typing import Dict, Any

pytestmark = pytest.mark.asyncio

async def test_create_automation_rule(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.post(
        "/api/v1/automation/rules",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Rule",
            "description": "A test rule",
            "trigger_event": "TICKET_CREATED",
            "conditions": [{"field": "priority", "operator": "eq", "value": "HIGH"}],
            "actions": [{"type": "SEND_EMAIL", "payload": {"to": "admin@test.com"}}]
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Test Rule"

async def test_update_automation_rule(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    # First create
    res = await client.post(
        "/api/v1/automation/rules",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Temp Rule",
            "trigger_event": "TICKET_CREATED",
            "conditions": [],
            "actions": []
        }
    )
    rule_id = res.json()["id"]

    # Update
    res = await client.put(
        f"/api/v1/automation/rules/{rule_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Updated Rule",
            "trigger_event": "TICKET_CREATED",
            "conditions": [],
            "actions": []
        }
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Rule"

async def test_get_unread_notifications(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200

async def test_mark_all_read(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.post(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert "marked as read" in res.json()["message"]

async def test_get_preferences(client: AsyncClient, admin_token: str, test_workspace: Dict[str, Any]):
    res = await client.get(
        "/api/v1/notifications/preferences",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "email_enabled" in data
