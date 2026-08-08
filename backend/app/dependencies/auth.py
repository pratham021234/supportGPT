from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.dependencies.db import get_db
from app.services.user_service import user_service
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedException("Could not validate credentials")
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Could not validate credentials")
        
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise UnauthorizedException("User not found")
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise UnauthorizedException("Inactive user")
    return current_user

def require_role(required_role: str):
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        roles = [r.role.name for r in current_user.roles]
        
        # OWNER has all permissions
        if "OWNER" in roles:
            return current_user
            
        if required_role not in roles:
            raise ForbiddenException(f"Require {required_role} role")
        return current_user
    return role_checker

require_owner = require_role("OWNER")
require_admin = require_role("ADMIN")
require_support = require_role("SUPPORT_AGENT")
