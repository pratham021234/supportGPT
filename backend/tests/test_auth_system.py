import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import auth_service
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.models.user import User

@pytest.mark.asyncio
async def test_register_duplicate_email(db_session: AsyncSession):
    with patch("app.repositories.user_repo.get_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = User(email="test@example.com")
        
        req = RegisterRequest(
            email="test@example.com",
            full_name="Test",
            password="StrongPassword1!",
            confirm_password="StrongPassword1!"
        )
        with pytest.raises(BadRequestException):
            await auth_service.register(db_session, req)

@pytest.mark.asyncio
async def test_login_invalid_password(db_session: AsyncSession):
    with patch("app.repositories.user_repo.get_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = User(email="test@example.com", password_hash="hash")
        
        req = LoginRequest(
            email="test@example.com",
            password="WrongPassword1!"
        )
        
        with patch("app.core.security.verify_password", return_value=False):
            with pytest.raises(UnauthorizedException):
                await auth_service.login(db_session, req)

@pytest.mark.asyncio
async def test_refresh_token_revoked(db_session: AsyncSession):
    with patch("app.core.security.decode_token") as mock_decode:
        mock_decode.return_value = {"sub": "user1", "type": "refresh"}
        with patch("app.repositories.refresh_token_repo.get_by_token_hash", new_callable=AsyncMock) as mock_get:
            # Return a token object with is_revoked=True
            mock_get.return_value = type('obj', (object,), {'is_revoked': True})()
            
            with pytest.raises(UnauthorizedException):
                await auth_service.refresh(db_session, "some_token")
