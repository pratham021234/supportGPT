from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import user_repo
from app.core.exceptions import NotFoundException
from typing import Optional
from app.models.user import User

class UserService:
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        user = await user_repo.get_with_roles(db, id=user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await user_repo.get_by_email(db, email=email)

    # Removed legacy assign_role_to_user as roles are now workspace-scopedrvice()

user_service = UserService()
