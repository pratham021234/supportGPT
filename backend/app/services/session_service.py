from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.session_repo import session_repo
from app.models.session import UserSession

class SessionService:
    async def create_session(
        self, db: AsyncSession, user_id: str, refresh_token: str, expires_at: str, 
        ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> UserSession:
        session_in = {
            "user_id": user_id,
            "refresh_token": refresh_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": expires_at,
            "last_active": datetime.utcnow().isoformat()
        }
        return await session_repo.create(db, obj_in=session_in)

    async def update_activity(self, db: AsyncSession, refresh_token: str) -> None:
        session = await session_repo.get_by_refresh_token(db, refresh_token)
        if session and not session.is_revoked:
            await session_repo.update(db, db_obj=session, obj_in={"last_active": datetime.utcnow().isoformat()})

    async def revoke_session(self, db: AsyncSession, refresh_token: str) -> None:
        session = await session_repo.get_by_refresh_token(db, refresh_token)
        if session:
            await session_repo.update(db, db_obj=session, obj_in={"is_revoked": True})

    async def revoke_all_sessions(self, db: AsyncSession, user_id: str) -> None:
        sessions = await session_repo.get_active_sessions(db, user_id)
        for session in sessions:
            await session_repo.update(db, db_obj=session, obj_in={"is_revoked": True})

session_service = SessionService()
