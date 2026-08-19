import pytest
from httpx import AsyncClient
from typing import Dict, Any
from app.models.widget import WidgetConfiguration

pytestmark = pytest.mark.asyncio

async def test_get_widget_config_public(client: AsyncClient, test_workspace: Dict[str, Any]):
    agent_id = test_workspace["agent_id"]
    res = await client.get(f"/api/v1/widget/config/{agent_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["theme"] == "light"
    assert "launcher_text" in data

async def test_widget_session_initialization(client: AsyncClient, test_workspace: Dict[str, Any]):
    # Init without identity
    res = await client.post(
        "/api/v1/widget/session",
        json={
            "workspace_id": test_workspace["id"],
            "agent_id": test_workspace["agent_id"]
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "session_token" in data
    
    session_token = data["session_token"]
    
    # Get history
    hist_res = await client.get(f"/api/v1/widget/history/{session_token}")
    assert hist_res.status_code == 200
    
    # Start conversation
    conv_res = await client.post(
        "/api/v1/widget/conversations",
        json={"session_token": session_token}
    )
    assert conv_res.status_code == 200
    assert "conversation_id" in conv_res.json()
    
    # Test handoff
    hand_res = await client.post(
        "/api/v1/widget/handoff",
        json={"session_token": session_token}
    )
    assert hand_res.status_code == 200

async def test_widget_session_identity(client: AsyncClient, test_workspace: Dict[str, Any]):
    # Init with identity
    res = await client.post(
        "/api/v1/widget/session",
        json={
            "workspace_id": test_workspace["id"],
            "agent_id": test_workspace["agent_id"],
            "customer_email": "widget_user@example.com",
            "customer_name": "Widget User"
        }
    )
    assert res.status_code == 200
    assert "session_token" in res.json()

async def test_widget_origin_validation(client: AsyncClient, test_workspace: Dict[str, Any], db_session):
    # Setup allowed domains
    config = WidgetConfiguration(
        workspace_id=test_workspace["id"],
        agent_id=test_workspace["agent_id"],
        allowed_domains=["allowed.com"]
    )
    db_session.add(config)
    await db_session.commit()
    
    # Should block unauthorized domain
    res1 = await client.post(
        "/api/v1/widget/session",
        json={
            "workspace_id": test_workspace["id"],
            "agent_id": test_workspace["agent_id"]
        },
        headers={"origin": "https://malicious.com"}
    )
    assert res1.status_code == 403
    
    # Should allow authorized domain
    res2 = await client.post(
        "/api/v1/widget/session",
        json={
            "workspace_id": test_workspace["id"],
            "agent_id": test_workspace["agent_id"]
        },
        headers={"origin": "https://app.allowed.com"}
    )
    assert res2.status_code == 200

async def test_widget_admin_settings(client: AsyncClient, test_workspace: Dict[str, Any]):
    res = await client.patch(
        "/api/v1/widget/settings",
        json={
            "primary_color": "#ff0000",
            "offline_message": "Sorry we are closed",
            "suggested_questions": ["Help"]
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["primary_color"] == "#ff0000"
    assert data["offline_message"] == "Sorry we are closed"
    assert "Help" in data["suggested_questions"]
