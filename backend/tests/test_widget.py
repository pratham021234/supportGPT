import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.v1.widget.router import initialize_session, SessionInitRequest
from app.services.widget.widget_service import widget_config_service, widget_session_service
from fastapi import HTTPException

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

@pytest.fixture
def agent_id():
    return str(uuid.uuid4())

@pytest.mark.asyncio
async def test_get_or_create_config(mock_db, workspace_id):
    with patch("app.repositories.widget_repo.widget_config_repo.get_by_workspace", return_value=None), \
         patch("app.repositories.widget_repo.widget_config_repo.create") as mock_create:
        
        mock_config = MagicMock()
        mock_config.workspace_id = workspace_id
        mock_config.theme = "light"
        mock_create.return_value = mock_config
        
        config = await widget_config_service.get_or_create_workspace_config(mock_db, workspace_id)
        assert config.workspace_id == workspace_id
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_initialize_anonymous_session(mock_db, workspace_id, agent_id):
    req = SessionInitRequest(workspace_id=workspace_id, agent_id=agent_id)
    
    with patch("app.services.widget.widget_service.widget_session_repo.create") as mock_create:
        mock_session = MagicMock()
        mock_session.session_token = "secure_token_123"
        mock_create.return_value = mock_session
        
        res = await initialize_session(req=req, origin=None, db=mock_db)
        
        assert res["session_token"] == "secure_token_123"

@pytest.mark.asyncio
async def test_initialize_identified_session(mock_db, workspace_id, agent_id):
    req = SessionInitRequest(
        workspace_id=workspace_id, 
        agent_id=agent_id,
        customer_email="test@example.com",
        customer_name="Test User"
    )
    
    mock_customer = MagicMock()
    mock_customer.id = uuid.uuid4()
    
    with patch("app.repositories.conversation_repo.customer_repo.get_by_email", return_value=mock_customer), \
         patch("app.services.widget.widget_service.widget_session_repo.create") as mock_create:
             
        mock_session = MagicMock()
        mock_session.session_token = "secure_token_456"
        mock_create.return_value = mock_session
        
        res = await initialize_session(req=req, origin=None, db=mock_db)
        assert res["session_token"] == "secure_token_456"
        mock_create.assert_called_once()
        
        # Verify customer_id was passed
        args, kwargs = mock_create.call_args
        obj_in = kwargs.get("obj_in")
        assert str(obj_in.customer_id) == str(mock_customer.id)

@pytest.mark.asyncio
async def test_initialize_session_origin_blocked(mock_db, workspace_id, agent_id):
    req = SessionInitRequest(workspace_id=workspace_id, agent_id=agent_id)
    
    with pytest.raises(HTTPException) as exc_info:
        await initialize_session(req=req, origin="https://malicious-site.com", db=mock_db)
        
    assert exc_info.value.status_code == 403
    assert "Origin not authorized" in exc_info.value.detail
