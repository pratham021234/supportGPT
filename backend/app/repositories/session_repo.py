from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.models.session import UserSession
from pydantic import BaseModel

class UserSessionCreate(BaseModel):
    user_id: str
    refresh_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: str

class UserSessionUpdate(BaseModel):
    is_revoked: Optional[bool] = None
    last_active: Optional[str] = None

class UserSessionRepository(BaseRepository[UserSession, UserSessionCreate, UserSessionUpdate]):
    async def get_by_refresh_token(self, db: AsyncSession, refresh_token: str) -> Optional[UserSession]:
        result = await db.execute(select(UserSession).filter(UserSession.refresh_token == refresh_token))
        return result.scalar_one_or_none()
        
    async def get_active_sessions(self, db: AsyncSession, user_id: str) -> List[UserSession]:
        result = await db.execute(
            select(UserSession).filter(
                UserSession.user_id == user_id, 
                UserSession.is_revoked == False
            )
        )
        return list(result.scalars().all())

session_repo = UserSessionRepository(UserSession)
