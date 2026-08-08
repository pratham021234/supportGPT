from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db
from app.dependencies.workspace import require_workspace_member
from app.models.workspace import WorkspaceMember
from app.core.exceptions import ForbiddenException

def require_permission(permission_name: str):
    async def permission_checker(
        member: WorkspaceMember = Depends(require_workspace_member),
        db: AsyncSession = Depends(get_db)
    ) -> WorkspaceMember:
        from app.services.permission_service import permission_service
        has_perm = await permission_service.has_permission(db, str(member.id), permission_name)
        if not has_perm:
            raise ForbiddenException(f"You lack the required permission: {permission_name}")
        return member
    return permission_checker
