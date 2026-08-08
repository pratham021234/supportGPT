import pytest
from httpx import AsyncClient
import uuid
from unittest.mock import AsyncMock, patch

from app.main import app

@pytest.mark.asyncio
async def test_health_check_live():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

@pytest.mark.asyncio
async def test_health_check_ready_success():
    with patch("app.api.v1.health.get_db") as mock_get_db, \
         patch("redis.asyncio.from_url") as mock_redis:
             
        # Mock DB execute
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        # Mock Redis ping
        mock_r = AsyncMock()
        mock_redis.return_value = mock_r
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health/ready")
            
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["dependencies"]["database"] == "ok"
        assert response.json()["dependencies"]["redis"] == "ok"

@pytest.mark.asyncio
async def test_health_check_ready_failure():
    with patch("app.api.v1.health.get_db") as mock_get_db, \
         patch("redis.asyncio.from_url") as mock_redis:
             
        # Mock DB execute to fail
        mock_db = AsyncMock()
        mock_db.execute.side_effect = Exception("DB Down")
        
        app.dependency_overrides[app.router.dependencies[0].dependency if app.router.dependencies else "none"] = lambda: mock_db
        # Actually in FastAPI dependencies are hard to mock via patch directly if injected. 
        # But this test covers the logic path if we force it.
        # For simplicity, we just mock the function being called inside the router or use dependency overrides.
        
        # We will use app.dependency_overrides for proper FastAPI mocking
        from app.dependencies.db import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        
        mock_r = AsyncMock()
        mock_r.ping.side_effect = Exception("Redis Down")
        mock_redis.return_value = mock_r
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health/ready")
            
        assert response.status_code == 503
        assert response.json()["status"] == "unready"
        assert response.json()["dependencies"]["database"] == "error"
        assert response.json()["dependencies"]["redis"] == "error"
        
        # Clean up
        app.dependency_overrides.clear()
