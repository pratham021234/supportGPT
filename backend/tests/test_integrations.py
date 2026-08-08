import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.integrations.sync_engine import sync_engine
from app.services.integrations.connectors import get_connector, SlackConnector
from app.models.notification import SystemEvent
from app.models.integration import SyncStatus, ConnectionStatus

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

def test_get_connector():
    connector = get_connector("slack")
    assert isinstance(connector, SlackConnector)
    
    with pytest.raises(ValueError):
        get_connector("unknown_provider")

@pytest.mark.asyncio
async def test_sync_engine_routes_correctly(mock_db, workspace_id):
    event = SystemEvent(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        event_type="TICKET_CREATED",
        payload={"ticket_id": "TKT-123", "title": "Help me"}
    )
    
    mock_conn = MagicMock()
    mock_conn.id = uuid.uuid4()
    mock_conn.provider = "hubspot"
    mock_conn.status = ConnectionStatus.CONNECTED
    
    mock_sync_log = MagicMock()
    mock_sync_log.id = uuid.uuid4()
    
    with patch("app.repositories.integration_repo.integration_conn_repo.get_by_workspace", return_value=[mock_conn]), \
         patch("app.repositories.integration_repo.integration_sync_repo.create", return_value=mock_sync_log), \
         patch("asyncio.create_task") as mock_create_task:
             
        await sync_engine.process_event(mock_db, event)
        
        # Verify sync log created
        mock_create_task.assert_called_once()
        
@pytest.mark.asyncio
async def test_sync_engine_push_and_update(workspace_id):
    mock_sync_log = MagicMock()
    mock_sync_log.id = uuid.uuid4()
    
    mock_connector = MagicMock()
    mock_connector.push_data = AsyncMock(return_value=True)
    
    with patch("app.repositories.integration_repo.integration_sync_repo.get", return_value=mock_sync_log), \
         patch("app.repositories.integration_repo.integration_sync_repo.update") as mock_update, \
         patch("app.services.integrations.sync_engine.SessionLocal"):
             
        await sync_engine._push_and_update(str(mock_sync_log.id), mock_connector, workspace_id, "ticket", "CREATE", {})
        
        # Verify push called
        mock_connector.push_data.assert_called_once()
        
        # Verify status updated to SUCCESS
        mock_update.assert_called_once()
        args, kwargs = mock_update.call_args
        obj_in = kwargs.get("obj_in")
        assert obj_in["status"] == SyncStatus.SUCCESS
