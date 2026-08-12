import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.services.messaging.conversation_engine import conversation_engine
from app.services.messaging.message_service import message_service
from app.services.handoff.human_handoff_service import human_handoff_service
from app.services.ticketing.ticket_creation_service import ticket_creation_service
from app.services.handoff.escalation_engine import escalation_engine
from app.models.conversation import ConversationStatus, SenderType

@pytest.mark.asyncio
async def test_conversation_lifecycle(db_session: AsyncSession):
    # Create
    conv = await conversation_engine.create_conversation(db_session, "ws1", "cust1")
    assert conv.status == ConversationStatus.OPEN
    
    # Store Message
    msg = await message_service.store_message(
        db_session, str(conv.id), SenderType.CUSTOMER, "Help me"
    )
    assert msg.content == "Help me"
    
    # Close
    closed_conv = await conversation_engine.close_conversation(db_session, str(conv.id))
    assert closed_conv.status == ConversationStatus.CLOSED

@pytest.mark.asyncio
async def test_escalation_engine_triggers(db_session: AsyncSession):
    # Create dummy conversation
    conv = await conversation_engine.create_conversation(db_session, "ws2", "cust2")
    
    # Trigger Escalation via low confidence
    with patch("app.services.handoff.human_handoff_service.human_handoff_service.trigger_handoff", new_callable=AsyncMock) as mock_handoff:
        with patch("app.services.ticketing.ticket_creation_service.ticket_creation_service.create_ai_escalation", new_callable=AsyncMock) as mock_ticket:
            with patch("app.services.notifications.notification_service.notification_service.notify_escalation", new_callable=AsyncMock) as mock_notify:
                
                escalated = await escalation_engine.evaluate_escalation(db_session, conv, confidence_score=50.0)
                
                assert escalated is True
                mock_handoff.assert_called_once()
                mock_ticket.assert_called_once()
                mock_notify.assert_called_once()
