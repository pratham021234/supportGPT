import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.services.notifications.notification_service import notification_service, event_bus
from app.services.automation.automation_service import automation_engine, ConditionEngine, ActionEngine
from app.models.notification import SystemEvent

@pytest.mark.asyncio
async def test_event_bus_publishing(db_session: AsyncSession):
    # Test that publishing an event routes it appropriately
    with patch("app.repositories.notification_repo.system_event_repo.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = SystemEvent(id="event1", event_type="TICKET_ASSIGNED", workspace_id="ws1")
        
        # Test just the putting logic in memory
        await event_bus.publish(db_session, "ws1", "TICKET_ASSIGNED")
        mock_create.assert_called_once()
        
@pytest.mark.asyncio
async def test_automation_condition_engine():
    engine = ConditionEngine()
    payload = {"confidence": 0.65}
    conditions = [{"field": "confidence", "operator": "lt", "value": 0.70}]
    
    # Should evaluate True since 0.65 < 0.70
    assert engine.evaluate(payload, conditions) is True
    
    conditions = [{"field": "confidence", "operator": "gt", "value": 0.70}]
    assert engine.evaluate(payload, conditions) is False

@pytest.mark.asyncio
async def test_automation_action_engine(db_session: AsyncSession):
    engine = ActionEngine()
    payload = {"customer_id": "cust1", "event_type": "TEST"}
    actions = [{"type": "CREATE_TICKET", "payload": {"title": "Test Alert"}}]
    
    with patch("app.repositories.ticket_repo.ticket_repo.create", new_callable=AsyncMock) as mock_create_ticket:
        logs = await engine.execute(db_session, "ws1", payload, actions)
        
        mock_create_ticket.assert_called_once()
        assert len(logs) == 1
        assert logs[0]["status"] == "SUCCESS"
        assert logs[0]["action"] == "CREATE_TICKET"

