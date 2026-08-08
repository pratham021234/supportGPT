import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from app.models.ticket import TicketPriority, TicketStatus, TicketSource, Ticket, SLAConfiguration
from app.services.ticketing.ticket_service import ticket_service, sla_service

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.ticketing.ticket_service.ticket_repo')
@patch('app.services.ticketing.ticket_service.ticket_activity_repo')
async def test_create_ai_escalation(mock_activity_repo, mock_ticket_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    customer_id = str(uuid.uuid4())
    
    mock_ticket = Ticket(
        id=uuid.uuid4(), 
        workspace_id=uuid.UUID(workspace_id),
        source=TicketSource.AI_ESCALATION,
        status=TicketStatus.OPEN
    )
    mock_ticket_repo.create = AsyncMock(return_value=mock_ticket)
    mock_activity_repo.create = AsyncMock()
    
    ticket = await ticket_service.create_ai_escalation(
        mock_db_session, 
        workspace_id, 
        conversation_id, 
        customer_id, 
        "Low Confidence: 45%"
    )
    
    assert ticket is not None
    assert mock_ticket_repo.create.called
    assert mock_activity_repo.create.called

@pytest.mark.asyncio
@patch('app.services.ticketing.ticket_service.sla_repo')
async def test_sla_breach_calculation(mock_sla_repo, mock_db_session):
    workspace_id = uuid.uuid4()
    
    mock_sla_config = SLAConfiguration(
        workspace_id=workspace_id,
        priority=TicketPriority.URGENT,
        first_response_minutes=60,
        resolution_minutes=240
    )
    
    mock_sla_repo.get_by_workspace = AsyncMock(return_value=[mock_sla_config])
    
    # Test ticket that is older than 60 mins but less than 240
    # Should breach first_response but not resolution
    mock_ticket = Ticket(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        priority=TicketPriority.URGENT,
        status=TicketStatus.OPEN,
        created_at=datetime.utcnow() - timedelta(minutes=90)
    )
    
    result = await sla_service.check_sla_breach(mock_db_session, mock_ticket)
    
    assert result["first_response_breached"] is True
    assert result["resolution_breached"] is False
    
    # Test ticket older than 240 mins
    # Should breach both
    mock_ticket_2 = Ticket(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        priority=TicketPriority.URGENT,
        status=TicketStatus.OPEN,
        created_at=datetime.utcnow() - timedelta(minutes=300)
    )
    
    result2 = await sla_service.check_sla_breach(mock_db_session, mock_ticket_2)
    assert result2["first_response_breached"] is True
    assert result2["resolution_breached"] is True
