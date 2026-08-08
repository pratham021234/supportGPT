from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.repositories.base import BaseRepository
from app.models.auth import RefreshToken, EmailVerification, PasswordReset

class RefreshTokenCreate(BaseModel):
    user_id: str
    token_hash: str
    expires_at: str

class RefreshTokenUpdate(BaseModel):
    is_revoked: bool

class RefreshTokenRepository(BaseRepository[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    async def get_by_token_hash(self, db: AsyncSession, *, token_hash: str) -> Optional[RefreshToken]:
        query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await db.execute(query)
        return result.scalars().first()

class EmailVerificationCreate(BaseModel):
    user_id: str
    token: str
    expires_at: str

class EmailVerificationUpdate(BaseModel):
    used: bool

class EmailVerificationRepository(BaseRepository[EmailVerification, EmailVerificationCreate, EmailVerificationUpdate]):
    async def get_by_token(self, db: AsyncSession, *, token: str) -> Optional[EmailVerification]:
        query = select(EmailVerification).where(EmailVerification.token == token)
        result = await db.execute(query)
        return result.scalars().first()

class PasswordResetCreate(BaseModel):
    user_id: str
    token: str
    expires_at: str

class PasswordResetUpdate(BaseModel):
    used: bool

class PasswordResetRepository(BaseRepository[PasswordReset, PasswordResetCreate, PasswordResetUpdate]):
    async def get_by_token(self, db: AsyncSession, *, token: str) -> Optional[PasswordReset]:
        query = select(PasswordReset).where(PasswordReset.token == token)
        result = await db.execute(query)
        return result.scalars().first()

refresh_token_repo = RefreshTokenRepository(RefreshToken)
email_verification_repo = EmailVerificationRepository(EmailVerification)
password_reset_repo = PasswordResetRepository(PasswordReset)
