import pytest
import uuid
from unittest.mock import AsyncMock, patch
from app.models.handoff import AgentPresenceStatus, AgentPresence, ConversationHandoff
from app.models.conversation import Conversation
from app.services.handoff.handoff_service import presence_service, handoff_service, ai_assist_service

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.handoff.handoff_service.presence_repo')
async def test_update_presence(mock_presence_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    mock_presence = AgentPresence(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        user_id=uuid.UUID(user_id),
        current_status=AgentPresenceStatus.ONLINE,
        active_conversations=0
    )
    
    # Test updating status
    mock_presence_repo.get_by_user = AsyncMock(return_value=mock_presence)
    mock_presence_repo.update = AsyncMock(return_value=mock_presence)
    
    result = await presence_service.update_status(mock_db_session, workspace_id, user_id, AgentPresenceStatus.AWAY)
    
    assert result is not None
    assert mock_presence_repo.update.called
    
@pytest.mark.asyncio
@patch('app.services.handoff.handoff_service.handoff_repo')
async def test_initiate_handoff(mock_handoff_repo, mock_db_session):
    conversation_id = str(uuid.uuid4())
    to_user_id = str(uuid.uuid4())
    
    mock_handoff = ConversationHandoff(
        id=uuid.uuid4(),
        conversation_id=uuid.UUID(conversation_id),
        to_user_id=uuid.UUID(to_user_id)
    )
    
    mock_handoff_repo.create = AsyncMock(return_value=mock_handoff)
    
    result = await handoff_service.initiate_handoff(
        mock_db_session, 
        conversation_id, 
        None, 
        to_user_id, 
        "Customer angry", 
        "SYSTEM"
    )
    
    assert result is not None
    assert mock_handoff_repo.create.called

@pytest.mark.asyncio
@patch('app.services.handoff.handoff_service.conversation_repo')
@patch('app.services.handoff.handoff_service.presence_repo')
async def test_accept_handoff(mock_presence_repo, mock_conversation_repo, mock_db_session):
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    mock_conv = Conversation(
        id=uuid.UUID(conversation_id),
        workspace_id=uuid.uuid4(),
        is_human_active=False
    )
    mock_presence = AgentPresence(
        id=uuid.uuid4(),
        active_conversations=1
    )
    
    mock_conversation_repo.get = AsyncMock(return_value=mock_conv)
    mock_conversation_repo.update = AsyncMock()
    
    mock_presence_repo.get_by_user = AsyncMock(return_value=mock_presence)
    mock_presence_repo.update = AsyncMock()
    
    success = await handoff_service.accept_handoff(mock_db_session, conversation_id, user_id)
    
    assert success is True
    assert mock_conversation_repo.update.called
    # Ensure active conversations was incremented
    assert mock_presence_repo.update.called

@pytest.mark.asyncio
async def test_ai_assist_summary(mock_db_session):
    # Testing the stub
    summary = await ai_assist_service.generate_summary(mock_db_session, "conv-123")
    assert "API rate limiting" in summary
