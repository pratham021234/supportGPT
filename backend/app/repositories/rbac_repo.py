from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.repositories.base import BaseRepository
from app.models.rbac import Permission, Role, RolePermission, UserWorkspaceRole
from app.schemas.team import RoleCreate, RoleUpdate

class RoleInternalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_id: Optional[str] = None
    is_system_role: bool = False

class RolePermissionCreate(BaseModel):
    role_id: str
    permission_id: str

class UserWorkspaceRoleCreate(BaseModel):
    workspace_member_id: str
    role_id: str
    assigned_by: Optional[str] = None

class PermissionRepository(BaseRepository[Permission, BaseModel, BaseModel]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Permission]:
        query = select(Permission).where(Permission.name == name)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(self, db: AsyncSession) -> List[Permission]:
        query = select(Permission)
        result = await db.execute(query)
        return result.scalars().all()

class RoleRepository(BaseRepository[Role, RoleInternalCreate, RoleUpdate]):
    async def get_by_name_and_workspace(self, db: AsyncSession, *, name: str, workspace_id: Optional[str]) -> Optional[Role]:
        query = select(Role).where(
            Role.name == name,
            Role.workspace_id == workspace_id
        ).options(selectinload(Role.permissions).selectinload(RolePermission.permission))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_system_roles(self, db: AsyncSession) -> List[Role]:
        query = select(Role).where(Role.is_system_role == True).options(
            selectinload(Role.permissions).selectinload(RolePermission.permission)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_workspace_roles(self, db: AsyncSession, workspace_id: str) -> List[Role]:
        query = select(Role).where(
            (Role.workspace_id == workspace_id) | (Role.is_system_role == True)
        ).options(
            selectinload(Role.permissions).selectinload(RolePermission.permission)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_permissions(self, db: AsyncSession, id: str) -> Optional[Role]:
        query = select(Role).where(Role.id == id).options(
            selectinload(Role.permissions).selectinload(RolePermission.permission)
        )
        result = await db.execute(query)
        return result.scalars().first()

class RolePermissionRepository(BaseRepository[RolePermission, RolePermissionCreate, BaseModel]):
    async def get_by_role(self, db: AsyncSession, role_id: str) -> List[RolePermission]:
        query = select(RolePermission).where(RolePermission.role_id == role_id).options(
            selectinload(RolePermission.permission)
        )
        result = await db.execute(query)
        return result.scalars().all()

class UserWorkspaceRoleRepository(BaseRepository[UserWorkspaceRole, UserWorkspaceRoleCreate, BaseModel]):
    async def get_by_member(self, db: AsyncSession, workspace_member_id: str) -> List[UserWorkspaceRole]:
        query = select(UserWorkspaceRole).where(
            UserWorkspaceRole.workspace_member_id == workspace_member_id
        ).options(
            selectinload(UserWorkspaceRole.role).selectinload(Role.permissions).selectinload(RolePermission.permission)
        )
        result = await db.execute(query)
        return result.scalars().all()
        
    async def delete_by_member(self, db: AsyncSession, workspace_member_id: str) -> None:
        roles = await self.get_by_member(db, workspace_member_id)
        for role in roles:
            await self.delete(db, id=str(role.id))

permission_repo = PermissionRepository(Permission)
role_repo = RoleRepository(Role)
role_permission_repo = RolePermissionRepository(RolePermission)
user_workspace_role_repo = UserWorkspaceRoleRepository(UserWorkspaceRole)
