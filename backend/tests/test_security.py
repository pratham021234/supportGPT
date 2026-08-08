import pytest
import uuid
import hashlib
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.security_service import generate_api_key, api_key_service, compliance_service
from app.models.security import AlertSeverity

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

@pytest.fixture
def user_id():
    return str(uuid.uuid4())

def test_generate_api_key():
    raw_key, key_hash, prefix = generate_api_key("test")
    
    # Check format
    assert raw_key.startswith("test_")
    assert prefix == "test"
    
    # Check hashing matches
    expected_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
    assert key_hash == expected_hash

@pytest.mark.asyncio
async def test_create_api_key(mock_db, workspace_id, user_id):
    with patch("app.repositories.security_repo.api_key_repo.create") as mock_create:
        mock_create.return_value = MagicMock(id=uuid.uuid4(), name="Test Key")
        
        db_key, raw_key = await api_key_service.create_key(mock_db, workspace_id, user_id, "Test Key", ["read:all"])
        
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        obj_in = kwargs.get("obj_in")
        
        assert obj_in.workspace_id == workspace_id
        assert obj_in.user_id == user_id
        assert obj_in.name == "Test Key"
        assert len(obj_in.scopes) == 1
        
        # Verify raw key matches the hash sent to DB
        expected_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
        assert obj_in.key_hash == expected_hash

@pytest.mark.asyncio
async def test_gdpr_export(mock_db, workspace_id, user_id):
    mock_user = MagicMock()
    mock_user.id = uuid.UUID(user_id)
    mock_user.email = "test@example.com"
    mock_user.full_name = "Test User"
    mock_user.created_at = datetime.utcnow()
    
    mock_ticket = MagicMock()
    mock_ticket.id = uuid.uuid4()
    mock_ticket.title = "Test Ticket"
    
    with patch("app.repositories.user_repo.user_repo.get", return_value=mock_user), \
         patch("app.repositories.ticket_repo.ticket_repo.get_by_workspace", return_value=[mock_ticket]):
             
        data = await compliance_service.export_user_data(mock_db, user_id, workspace_id)
        
        assert data["user"]["email"] == "test@example.com"
        assert len(data["tickets"]) == 1
        assert data["tickets"][0]["title"] == "Test Ticket"
        assert "exported_at" in data

@pytest.mark.asyncio
async def test_gdpr_delete(mock_db, user_id):
    mock_user = MagicMock()
    mock_user.id = uuid.UUID(user_id)
    
    mock_session = MagicMock()
    
    with patch("app.repositories.user_repo.user_repo.get", return_value=mock_user), \
         patch("app.repositories.user_repo.user_repo.update") as mock_user_update, \
         patch("app.repositories.session_repo.user_session_repo.get_active_by_user", return_value=[mock_session]), \
         patch("app.repositories.session_repo.user_session_repo.update") as mock_session_update:
             
        await compliance_service.delete_user_data(mock_db, user_id)
        
        # User is anonymized
        mock_user_update.assert_called_once()
        args, kwargs = mock_user_update.call_args
        obj_in = kwargs.get("obj_in")
        assert "anonymized.com" in obj_in["email"]
        assert obj_in["is_active"] == False
        
        # Sessions are revoked
        mock_session_update.assert_called_once()
        args, kwargs = mock_session_update.call_args
        obj_in = kwargs.get("obj_in")
        assert obj_in["is_revoked"] == True
