import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.analytics.analytics_service import (
    metrics_service, knowledge_gap_service, knowledge_intelligence
)
from app.services.analytics.insights_engine import insights_engine
from app.models.analytics import GapStatus

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

@pytest.mark.asyncio
async def test_dashboard_metrics(mock_db, workspace_id):
    with patch("app.repositories.conversation_repo.conversation_repo.get_by_workspace", return_value=[MagicMock(), MagicMock()]), \
         patch("app.repositories.ticket_repo.ticket_repo.get_by_workspace", return_value=[MagicMock()]), \
         patch("app.repositories.analytics_repo.analytics_event_repo.count_by_type", side_effect=[10, 100]), \
         patch("app.repositories.analytics_repo.knowledge_gap_repo.get_by_workspace", return_value=[]):
             
        # 10 escalations, 100 AI queries -> AI Res Rate = 90%
        # Knowledge gaps = 0 -> coverage = 100%
        
        metrics = await metrics_service.get_dashboard_metrics(mock_db, workspace_id)
        
        assert metrics["total_conversations"] == 2
        assert metrics["total_tickets"] == 1
        assert metrics["total_escalations"] == 10
        assert metrics["ai_resolution_rate"] == 90.0
        assert metrics["knowledge_coverage"] == 100.0

@pytest.mark.asyncio
async def test_insights_engine_fallback(mock_db, workspace_id):
    mock_gap = MagicMock()
    mock_gap.status = GapStatus.OPEN
    mock_gap.query = "How to configure SAML"
    mock_gap.occurrences = 5
    mock_gap.confidence_average = 0.2
    mock_gap.escalation_count = 3
    
    with patch("app.repositories.analytics_repo.knowledge_gap_repo.get_by_workspace", return_value=[mock_gap]):
        with patch.object(insights_engine.model, 'generate_content', return_value=MagicMock(text='[{"title": "SAML Configuration", "description": "Missing docs", "action": "Write guide", "impact": "HIGH"}]')):
            insights = await insights_engine.generate_knowledge_recommendations(mock_db, workspace_id)
            assert len(insights) > 0
            assert "SAML" in insights[0]["title"]

@pytest.mark.asyncio
async def test_knowledge_gap_service(mock_db, workspace_id):
    # Test tracking a new gap
    with patch("app.repositories.analytics_repo.knowledge_gap_repo.get_by_workspace", return_value=[]), \
         patch("app.repositories.analytics_repo.knowledge_gap_repo.create") as mock_create:
             
        await knowledge_gap_service.process_failed_query(mock_db, workspace_id, "Unknown API error", 0.1)
        mock_create.assert_called_once()
        
    # Test updating an existing gap
    mock_gap = MagicMock()
    mock_gap.query = "Unknown API error"
    mock_gap.status = GapStatus.OPEN
    mock_gap.occurrences = 1
    mock_gap.confidence_average = 0.1
    mock_gap.escalation_count = 1
    
    with patch("app.repositories.analytics_repo.knowledge_gap_repo.get_by_workspace", return_value=[mock_gap]), \
         patch("app.repositories.analytics_repo.knowledge_gap_repo.update") as mock_update:
             
        await knowledge_gap_service.process_failed_query(mock_db, workspace_id, "Unknown API error", 0.5)
        mock_update.assert_called_once()
        
        args, kwargs = mock_update.call_args
        obj_in = kwargs.get("obj_in")
        assert obj_in["occurrences"] == 2
        assert obj_in["confidence_average"] == 0.3 # (0.1 + 0.5)/2
        assert obj_in["escalation_count"] == 2
