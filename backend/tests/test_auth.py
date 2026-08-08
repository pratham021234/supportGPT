import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app
from app.dependencies import get_db

client = TestClient(app)

# Override get_db dependency
async def override_get_db():
    yield AsyncMock()

app.dependency_overrides[get_db] = override_get_db

# Patch rate limiter to avoid redis dependency during basic auth tests
@pytest.fixture(autouse=True)
def mock_rate_limiter():
    with patch("fastapi_limiter.depends.RateLimiter.__call__", return_value=None):
        yield

def test_password_policy_validation():
    # Test valid password
    from app.schemas.auth import RegisterRequest
    req = RegisterRequest(email="test@test.com", full_name="Test", password="Password123!", confirm_password="Password123!")
    assert req.password == "Password123!"

    # Test invalid passwords
    with pytest.raises(ValueError):
        RegisterRequest(email="test@test.com", full_name="Test", password="short", confirm_password="short")
    
    with pytest.raises(ValueError):
        RegisterRequest(email="test@test.com", full_name="Test", password="nouppercase1!", confirm_password="nouppercase1!")
        
    with pytest.raises(ValueError):
        RegisterRequest(email="test@test.com", full_name="Test", password="NOLOWERCASE1!", confirm_password="NOLOWERCASE1!")

@patch("app.services.auth_service.auth_service.register")
def test_register_endpoint(mock_register):
    # Mock return value
    mock_user = AsyncMock()
    mock_user.id = "123e4567-e89b-12d3-a456-426614174000"
    mock_user.email = "test@test.com"
    mock_user.full_name = "Test"
    mock_user.is_verified = False
    mock_user.is_active = True
    mock_user.roles = []
    mock_user.created_at = "2024-01-01T00:00:00Z"
    mock_user.updated_at = "2024-01-01T00:00:00Z"
    mock_register.return_value = mock_user

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "full_name": "Test User",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "test@test.com" in data["data"]["email"]

@patch("app.services.auth_service.auth_service.login")
def test_login_endpoint(mock_login):
    mock_user = AsyncMock()
    mock_user.id = "123e4567-e89b-12d3-a456-426614174000"
    mock_user.email = "test@test.com"
    mock_user.full_name = "Test"
    mock_user.is_verified = True
    mock_user.is_active = True
    mock_user.roles = []
    mock_user.created_at = "2024-01-01T00:00:00Z"
    mock_user.updated_at = "2024-01-01T00:00:00Z"
    
    mock_login.return_value = ("access_token_mock", "refresh_token_mock", mock_user)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@test.com",
            "password": "StrongPassword123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["access_token"] == "access_token_mock"

@patch("app.services.auth_service.auth_service.logout_all")
def test_logout_all_endpoint(mock_logout_all):
    mock_logout_all.return_value = True
    
    # We must mock get_current_active_user for this to work
    mock_user = AsyncMock()
    mock_user.id = "123e4567-e89b-12d3-a456-426614174000"
    
    from app.dependencies.auth import get_current_active_user
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    
    response = client.post("/api/v1/auth/logout-all")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Cleanup override
    app.dependency_overrides.pop(get_current_active_user, None)
