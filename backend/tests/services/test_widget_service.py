import pytest
import uuid
from unittest.mock import AsyncMock, patch
from app.models.widget import WidgetConfiguration, WidgetSession
from app.services.widget.widget_service import widget_config_service, widget_session_service

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.widget.widget_service.widget_config_repo')
async def test_get_or_create_config_existing(mock_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    mock_config = WidgetConfiguration(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        theme="dark"
    )
    
    mock_repo.get_by_workspace = AsyncMock(return_value=mock_config)
    
    result = await widget_config_service.get_or_create_workspace_config(mock_db_session, workspace_id)
    
    assert result.theme == "dark"
    assert not mock_repo.create.called

@pytest.mark.asyncio
@patch('app.services.widget.widget_service.widget_config_repo')
async def test_get_or_create_config_new(mock_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    mock_repo.get_by_workspace = AsyncMock(return_value=None)
    mock_repo.create = AsyncMock(return_value=WidgetConfiguration(workspace_id=uuid.UUID(workspace_id)))
    
    result = await widget_config_service.get_or_create_workspace_config(mock_db_session, workspace_id)
    
    assert mock_repo.create.called
    assert result is not None

@pytest.mark.asyncio
@patch('app.services.widget.widget_service.widget_session_repo')
async def test_initialize_session(mock_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())
    
    mock_session = WidgetSession(
        id=uuid.uuid4(),
        session_token="test_token_123"
    )
    mock_repo.create = AsyncMock(return_value=mock_session)
    
    result = await widget_session_service.initialize_session(mock_db_session, workspace_id, agent_id)
    
    assert result.session_token == "test_token_123"
    assert mock_repo.create.called

@pytest.mark.asyncio
@patch('app.services.widget.widget_service.widget_session_repo')
@patch('app.services.widget.widget_service.conversation_repo')
@patch('app.services.widget.widget_service.customer_repo')
async def test_start_conversation(mock_customer_repo, mock_conv_repo, mock_session_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    mock_session = WidgetSession(
        workspace_id=uuid.UUID(workspace_id),
        agent_id=None,
        customer_id=None,
        session_token="token"
    )
    
    class MockConv:
        id = uuid.uuid4()
        
    class MockCust:
        id = uuid.uuid4()
        
    mock_session_repo.get_by_token = AsyncMock(return_value=mock_session)
    mock_customer_repo.create = AsyncMock(return_value=MockCust())
    mock_session_repo.update = AsyncMock(return_value=mock_session)
    mock_conv_repo.create = AsyncMock(return_value=MockConv())
    
    conv_id = await widget_session_service.start_conversation(mock_db_session, "token")
    
    assert conv_id is not None
    assert mock_conv_repo.create.called
