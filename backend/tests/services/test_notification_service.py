import pytest
import uuid
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.notification import SystemEvent, NotificationPreference
from app.services.notifications.notification_service import event_bus, notification_service, preference_service

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.notifications.notification_service.system_event_repo')
async def test_event_bus_publish(mock_sys_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    mock_event = SystemEvent(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        event_type="TEST_EVENT"
    )
    mock_sys_repo.create = AsyncMock(return_value=mock_event)
    
    # ensure queue is empty
    while not event_bus._queue.empty():
        event_bus._queue.get_nowait()
        
    await event_bus.publish(mock_db_session, workspace_id, "TEST_EVENT")
    
    assert mock_sys_repo.create.called
    assert not event_bus._queue.empty()
    
@pytest.mark.asyncio
@patch('app.services.notifications.notification_service.notification_repo')
@patch('app.services.notifications.notification_service.delivery_service')
@patch('app.services.notifications.notification_service.preference_service')
async def test_notification_rule_engine(mock_pref_service, mock_delivery, mock_notif_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    mock_event = SystemEvent(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        event_type="TICKET_ASSIGNED",
        payload={"assigned_to": user_id}
    )
    
    mock_pref = NotificationPreference(
        in_app_enabled=True,
        email_enabled=True
    )
    mock_pref_service.get_preferences = AsyncMock(return_value=mock_pref)
    mock_notif_repo.create = AsyncMock(return_value=MagicMock())
    
    mock_delivery.dispatch_in_app = AsyncMock()
    mock_delivery.dispatch_email = AsyncMock()
    
    await notification_service.process_event(mock_db_session, mock_event)
    
    assert mock_notif_repo.create.called
    assert mock_delivery.dispatch_in_app.called
    assert mock_delivery.dispatch_email.called

@pytest.mark.asyncio
@patch('app.services.notifications.notification_service.preference_repo')
async def test_update_preferences(mock_pref_repo, mock_db_session):
    user_id = str(uuid.uuid4())
    mock_pref = NotificationPreference(user_id=uuid.UUID(user_id))
    
    mock_pref_repo.get_by_user = AsyncMock(return_value=mock_pref)
    mock_pref_repo.update = AsyncMock(return_value=mock_pref)
    
    result = await preference_service.update_preferences(mock_db_session, user_id, {"in_app_enabled": False})
    
    assert result is not None
    assert mock_pref_repo.update.called
