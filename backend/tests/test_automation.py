import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.automation.automation_service import ConditionEngine, ActionEngine, automation_engine
from app.models.notification import SystemEvent

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

def test_condition_engine_equals():
    engine = ConditionEngine()
    payload = {"confidence": 0.5, "source": "web"}
    
    # Should match
    assert engine.evaluate(payload, [{"field": "source", "operator": "eq", "value": "web"}]) == True
    # Should fail
    assert engine.evaluate(payload, [{"field": "source", "operator": "eq", "value": "api"}]) == False

def test_condition_engine_less_than():
    engine = ConditionEngine()
    payload = {"confidence": 0.5}
    
    # 0.5 < 0.6 -> True
    assert engine.evaluate(payload, [{"field": "confidence", "operator": "lt", "value": 0.6}]) == True
    # 0.5 < 0.4 -> False
    assert engine.evaluate(payload, [{"field": "confidence", "operator": "lt", "value": 0.4}]) == False

def test_condition_engine_contains():
    engine = ConditionEngine()
    payload = {"query": "How do I reset my password?"}
    
    assert engine.evaluate(payload, [{"field": "query", "operator": "contains", "value": "password"}]) == True
    assert engine.evaluate(payload, [{"field": "query", "operator": "contains", "value": "billing"}]) == False

@pytest.mark.asyncio
async def test_action_engine_create_ticket(mock_db, workspace_id):
    engine = ActionEngine()
    payload = {"event_type": "LOW_CONFIDENCE", "customer_id": str(uuid.uuid4())}
    actions = [{"type": "CREATE_TICKET", "payload": {"priority": "HIGH"}}]
    
    with patch("app.repositories.ticket_repo.ticket_repo.create") as mock_create:
        logs = await engine.execute(mock_db, workspace_id, payload, actions)
        
        assert len(logs) == 1
        assert logs[0]["status"] == "SUCCESS"
        assert logs[0]["action"] == "CREATE_TICKET"
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_action_engine_send_email(mock_db, workspace_id):
    engine = ActionEngine()
    payload = {"event_type": "ESCALATION"}
    actions = [{"type": "SEND_EMAIL", "payload": {"to": "admin@example.com", "subject": "Alert"}}]
    
    with patch("app.services.email_service.email_service.send_email") as mock_send:
        logs = await engine.execute(mock_db, workspace_id, payload, actions)
        
        assert len(logs) == 1
        assert logs[0]["status"] == "SUCCESS"
        mock_send.assert_called_once_with("admin@example.com", "Alert", str(payload))

@pytest.mark.asyncio
async def test_automation_engine_process_event(mock_db, workspace_id):
    event = SystemEvent(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        event_type="LOW_CONFIDENCE",
        payload={"confidence": 0.4, "customer_id": str(uuid.uuid4())}
    )
    
    mock_rule = MagicMock()
    mock_rule.id = uuid.uuid4()
    mock_rule.workspace_id = event.workspace_id
    mock_rule.conditions = [{"field": "confidence", "operator": "lt", "value": 0.6}]
    mock_rule.actions = [{"type": "CREATE_TICKET", "payload": {}}]
    
    with patch("app.repositories.automation_repo.automation_rule_repo.get_active_by_trigger", return_value=[mock_rule]), \
         patch("app.repositories.ticket_repo.ticket_repo.create") as mock_ticket_create, \
         patch("app.repositories.automation_repo.workflow_execution_repo.create") as mock_exec_create:
             
        await automation_engine.process_event(mock_db, event)
        
        # Action should have fired
        mock_ticket_create.assert_called_once()
        # Execution should be logged
        mock_exec_create.assert_called_once()
        
        args, kwargs = mock_exec_create.call_args
        obj_in = kwargs.get("obj_in")
        assert obj_in.status.value == "SUCCESS"
        assert obj_in.rule_id == str(mock_rule.id)
