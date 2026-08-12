import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.services.widget.widget_service import widget_config_service, widget_session_service
from app.services.widget.widget_health_service import widget_health_service

@pytest.mark.asyncio
async def test_get_or_create_workspace_config(db_session: AsyncSession):
    with patch("app.repositories.widget_repo.widget_config_repo.get_by_workspace", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None # Force create
        
        with patch("app.repositories.widget_repo.widget_config_repo.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = "CREATED_CONFIG"
            
            result = await widget_config_service.get_or_create_workspace_config(db_session, "ws1")
            assert result == "CREATED_CONFIG"
            mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_widget_session_initialization(db_session: AsyncSession):
    with patch("app.repositories.widget_repo.widget_session_repo.create", new_callable=AsyncMock) as mock_create:
        
        with patch("app.services.analytics.analytics_service.AnalyticsEventService.log_event", new_callable=AsyncMock) as mock_log:
            mock_create.return_value = type('obj', (object,), {'id': 'sess1'})()
            
            result = await widget_session_service.initialize_session(db_session, "ws1", "agent1")
            
            assert result.id == "sess1"
            mock_create.assert_called_once()

def test_widget_health_service():
    health = widget_health_service.get_widget_health()
    assert health["status"] == "HEALTHY"
    assert "cdn_latency_ms" in health
