import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
import json

from app.services.analytics.analytics_cache_service import analytics_cache_service, cached_analytics
from app.services.analytics.trend_analysis_service import trend_analysis_service
from app.services.analytics.insights_engine import insights_engine

@pytest.mark.asyncio
async def test_analytics_caching():
    # Test setting and getting from the local mock cache
    await analytics_cache_service.set("test_key", {"metric": 100})
    val = await analytics_cache_service.get("test_key")
    assert val is not None
    assert val["metric"] == 100

def test_trend_analysis_growth():
    result = trend_analysis_service.calculate_trend_percentage(150, 100)
    assert result == "+50.0% from last period"
    
def test_trend_analysis_decline():
    result = trend_analysis_service.calculate_trend_percentage(80, 100)
    assert result == "-20.0% from last period"
    
def test_anomaly_detection():
    data = [10, 12, 11, 13, 9, 100, 10, 11]
    anomalies = trend_analysis_service.detect_anomalies(data)
    assert len(anomalies) == 1
    assert anomalies[0]["value"] == 100

@pytest.mark.asyncio
async def test_business_insights_engine_fallback(db_session: AsyncSession):
    # When no model is configured, it should return the fallback
    with patch("app.repositories.analytics_repo.knowledge_gap_repo.get_by_workspace", new_callable=AsyncMock) as mock_get:
        from app.models.analytics import KnowledgeGap, GapStatus
        mock_get.return_value = [
            KnowledgeGap(query="How to reset password?", occurrences=5, status=GapStatus.OPEN)
        ]
        
        # Ensure model is None
        insights_engine.model = None
        
        recommendations = await insights_engine.generate_knowledge_recommendations(db_session, "ws1")
        assert len(recommendations) == 1
        assert recommendations[0]["impact"] == "HIGH"
        assert "How to reset password" in recommendations[0]["description"]
