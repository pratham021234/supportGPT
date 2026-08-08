import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch, MagicMock

from app.models.conversation import ConversationStatus, SenderType, CustomerFeedback
from app.models.ticket import TicketStatus, TicketSource
from app.services.messaging.realtime_service import realtime_messaging_service
from app.services.messaging.conversation_service import conversation_service
from app.services.ticketing.ticket_service import ticket_service
from app.services.handoff.handoff_service import handoff_service

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

@pytest.fixture
def conversation_id():
    return str(uuid.uuid4())

@pytest.fixture
def agent_id():
    return str(uuid.uuid4())

@pytest.fixture
def customer_id():
    return str(uuid.uuid4())

@pytest.mark.asyncio
async def test_escalation_workflow(mock_db, workspace_id, conversation_id, agent_id, customer_id):
    # Setup mocks
    mock_websocket = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    mock_conv = MagicMock()
    mock_conv.id = conversation_id
    mock_conv.workspace_id = workspace_id
    mock_conv.agent_id = agent_id
    mock_conv.customer_id = customer_id
    mock_conv.is_human_active = False
    
    mock_ticket = MagicMock()
    mock_ticket.id = uuid.uuid4()
    
    # 1. RAG triggers escalation due to low confidence
    with patch("app.services.messaging.conversation_service.conversation_service.get_conversation", return_value=mock_conv), \
         patch("app.services.messaging.conversation_service.conversation_service.add_message", return_value=AsyncMock()), \
         patch("app.services.agent.testing_service.agent_testing_service.test_agent", return_value={"answer": "I don't know.", "confidence_score": 42.0, "escalate": True}), \
         patch("app.services.messaging.conversation_service.conversation_service.update_status", return_value=mock_conv) as mock_update_status, \
         patch("app.services.handoff.handoff_service.handoff_service.initiate_handoff", return_value=AsyncMock()) as mock_handoff, \
         patch("app.services.ticketing.ticket_service.ticket_service.create_ai_escalation", return_value=mock_ticket) as mock_create_ticket:
         
        await realtime_messaging_service.handle_customer_message(
            db=mock_db,
            websocket=mock_websocket,
            conversation_id=conversation_id,
            text="I cannot access my account.",
            user_id="test_user"
        )
        
        # Verify status changed to ESCALATED
        mock_update_status.assert_called_once_with(mock_db, conversation_id, ConversationStatus.ESCALATED)
        
        # Verify Handoff initiated
        mock_handoff.assert_called_once()
        
        # Verify Ticket Created
        mock_create_ticket.assert_called_once_with(
            db=mock_db,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            reason="AI Escalation triggered. Last query: I cannot access my account."
        )

@pytest.mark.asyncio
async def test_assign_and_resolve_ticket(mock_db):
    ticket_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    mock_ticket = MagicMock()
    mock_ticket.id = ticket_id
    
    # Test assignment
    with patch("app.repositories.ticket_repo.ticket_repo.get", return_value=mock_ticket), \
         patch("app.repositories.ticket_repo.ticket_repo.update", return_value=mock_ticket), \
         patch("app.repositories.ticket_repo.ticket_activity_repo.create", return_value=AsyncMock()):
        
        res = await ticket_service.assign_ticket(mock_db, ticket_id, user_id, user_id)
        assert res is not None

    # Test resolution
    with patch("app.repositories.ticket_repo.ticket_repo.get", return_value=mock_ticket), \
         patch("app.repositories.ticket_repo.ticket_repo.update", return_value=mock_ticket), \
         patch("app.repositories.ticket_repo.ticket_activity_repo.create", return_value=AsyncMock()):
         
        res = await ticket_service.update_status(mock_db, ticket_id, TicketStatus.RESOLVED, user_id)
        assert res is not None

@pytest.mark.asyncio
async def test_customer_feedback(mock_db, conversation_id):
    mock_fb = CustomerFeedback(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        is_helpful=True,
        rating=5,
        comment="Great support!"
    )
    
    with patch("app.repositories.conversation_repo.customer_feedback_repo.create", return_value=mock_fb):
        fb = await conversation_service.add_feedback(mock_db, conversation_id, True, 5, "Great support!")
        assert fb.is_helpful == True
        assert fb.rating == 5
