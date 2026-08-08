import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.models.user import User

@pytest.fixture
def auth_service():
    return AuthService()

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_register_existing_email(auth_service, mock_db):
    with patch("app.services.auth_service.user_repo") as mock_user_repo:
        mock_user_repo.get_by_email = AsyncMock(return_value=User(email="test@test.com"))
        
        request = RegisterRequest(
            email="test@test.com",
            full_name="Test User",
            password="Password1!",
            confirm_password="Password1!"
        )
        
        with pytest.raises(BadRequestException) as exc:
            await auth_service.register(mock_db, request)
            
        assert "Email already registered" in str(exc.value.message)

@pytest.mark.asyncio
async def test_register_success(auth_service, mock_db):
    with patch("app.services.auth_service.user_repo") as mock_user_repo, \
         patch("app.services.auth_service.user_service") as mock_user_service, \
         patch("app.services.auth_service.email_verification_repo") as mock_ev_repo, \
         patch("app.services.auth_service.email_service") as mock_email_service:
         
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        new_user = User(id="123e4567-e89b-12d3-a456-426614174000", email="test@test.com")
        mock_user_repo.create = AsyncMock(return_value=new_user)
        mock_user_repo.get_with_roles = AsyncMock(return_value=new_user)
        mock_user_service.assign_role = AsyncMock()
        mock_ev_repo.create = AsyncMock()
        mock_email_service.send_verification_email = AsyncMock()
        
        request = RegisterRequest(
            email="test@test.com",
            full_name="Test User",
            password="Password1!",
            confirm_password="Password1!"
        )
        
        result = await auth_service.register(mock_db, request)
        
        assert result.email == "test@test.com"
        mock_user_service.assign_role.assert_called_once_with(mock_db, str(new_user.id), "OWNER")
        mock_email_service.send_verification_email.assert_called_once()

@pytest.mark.asyncio
async def test_login_invalid_email(auth_service, mock_db):
    with patch("app.services.auth_service.user_repo") as mock_user_repo:
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        
        request = LoginRequest(email="test@test.com", password="Password1!")
        
        with pytest.raises(UnauthorizedException):
            await auth_service.login(mock_db, request)
