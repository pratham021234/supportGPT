import pytest
from unittest.mock import AsyncMock, patch
from app.models.conversation import ConversationStatus, SenderType, Customer, Conversation
from app.services.messaging.conversation_service import conversation_service, customer_service
import uuid

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.messaging.conversation_service.customer_repo')
async def test_get_or_create_customer(mock_customer_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    email = "test@example.com"
    
    mock_customer = Customer(id=uuid.uuid4(), workspace_id=uuid.UUID(workspace_id), email=email)
    
    # Test new customer
    mock_customer_repo.get_by_email = AsyncMock(return_value=None)
    mock_customer_repo.create = AsyncMock(return_value=mock_customer)
    
    customer = await customer_service.get_or_create_customer(mock_db_session, workspace_id, email, "Test User")
    
    assert customer is not None
    assert mock_customer_repo.create.called
    
    # Test existing customer
    mock_customer_repo.get_by_email = AsyncMock(return_value=mock_customer)
    mock_customer_repo.update = AsyncMock(return_value=mock_customer)
    
    customer = await customer_service.get_or_create_customer(mock_db_session, workspace_id, email, "Test User")
    
    assert mock_customer_repo.update.called

@pytest.mark.asyncio
@patch('app.services.messaging.conversation_service.conversation_repo')
@patch('app.services.messaging.conversation_service.conversation_event_repo')
async def test_create_conversation(mock_event_repo, mock_conv_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    customer_id = str(uuid.uuid4())
    
    mock_conv = Conversation(id=uuid.uuid4(), workspace_id=uuid.UUID(workspace_id), customer_id=uuid.UUID(customer_id))
    
    mock_conv_repo.create = AsyncMock(return_value=mock_conv)
    mock_event_repo.create = AsyncMock()
    
    conv = await conversation_service.create_conversation(mock_db_session, workspace_id, customer_id)
    
    assert conv is not None
    assert mock_conv_repo.create.called
    assert mock_event_repo.create.called

@pytest.mark.asyncio
@patch('app.services.messaging.conversation_service.conversation_repo')
@patch('app.services.messaging.conversation_service.message_repo')
async def test_add_message(mock_msg_repo, mock_conv_repo, mock_db_session):
    conv_id = str(uuid.uuid4())
    customer_id = str(uuid.uuid4())
    
    mock_msg_repo.create = AsyncMock()
    mock_conv_repo.update_last_message = AsyncMock()
    
    await conversation_service.add_message(
        mock_db_session, 
        conversation_id=conv_id, 
        sender_type=SenderType.CUSTOMER, 
        content="Hello!", 
        sender_id=customer_id
    )
    
    assert mock_msg_repo.create.called
    assert mock_conv_repo.update_last_message.called
