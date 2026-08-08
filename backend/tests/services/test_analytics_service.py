import pytest
import uuid
from unittest.mock import AsyncMock, patch
from app.models.analytics import KnowledgeGap, GapStatus
from app.services.analytics.analytics_service import knowledge_gap_service, metrics_service

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.analytics.analytics_service.knowledge_gap_repo')
async def test_process_failed_query_new(mock_gap_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    query = "How to reset password?"
    confidence = 0.4
    
    mock_gap_repo.get_by_workspace = AsyncMock(return_value=[])
    mock_gap_repo.create = AsyncMock()
    
    await knowledge_gap_service.process_failed_query(mock_db_session, workspace_id, query, confidence)
    
    assert mock_gap_repo.create.called

@pytest.mark.asyncio
@patch('app.services.analytics.analytics_service.knowledge_gap_repo')
async def test_process_failed_query_existing(mock_gap_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    query = "How to reset password?"
    
    existing_gap = KnowledgeGap(
        id=uuid.uuid4(),
        workspace_id=uuid.UUID(workspace_id),
        query=query,
        occurrences=2,
        confidence_average=0.5,
        escalation_count=1,
        status=GapStatus.OPEN
    )
    
    mock_gap_repo.get_by_workspace = AsyncMock(return_value=[existing_gap])
    mock_gap_repo.update = AsyncMock()
    
    await knowledge_gap_service.process_failed_query(mock_db_session, workspace_id, query, 0.3)
    
    assert mock_gap_repo.update.called

@pytest.mark.asyncio
@patch('app.services.analytics.analytics_service.conversation_repo')
@patch('app.services.analytics.analytics_service.ticket_repo')
@patch('app.services.analytics.analytics_service.analytics_event_repo')
async def test_get_dashboard_metrics(mock_event_repo, mock_ticket_repo, mock_conversation_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    mock_conversation_repo.get_by_workspace = AsyncMock(return_value=[1, 2, 3]) # 3 convos
    mock_ticket_repo.get_by_workspace = AsyncMock(return_value=[1]) # 1 ticket
    
    # 10 queries, 2 escalations -> 80% resolution rate
    async def mock_count_by_type(db, ws_id, ev_type):
        if ev_type == "RAG_QUERY":
            return 10
        elif ev_type == "AI_ESCALATION":
            return 2
        return 0
        
    mock_event_repo.count_by_type = AsyncMock(side_effect=mock_count_by_type)
    
    metrics = await metrics_service.get_dashboard_metrics(mock_db_session, workspace_id)
    
    assert metrics["total_conversations"] == 3
    assert metrics["total_tickets"] == 1
    assert metrics["ai_resolution_rate"] == 80.0
    assert metrics["total_escalations"] == 2
