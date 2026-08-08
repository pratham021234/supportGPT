from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceAuditLog
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceMemberUpdate,
    WorkspaceInvitationCreate
)
from pydantic import BaseModel
import uuid

# Additional internal schemas for repositories that need more fields than the public schemas
class WorkspaceInternalCreate(WorkspaceCreate):
    slug: str
    owner_id: str

class WorkspaceMemberCreate(BaseModel):
    workspace_id: str
    user_id: str
    status: str = "ACTIVE"

class WorkspaceInvitationInternalCreate(WorkspaceInvitationCreate):
    workspace_id: str
    token: str
    expires_at: str
    invited_by: str

class WorkspaceAuditLogCreate(BaseModel):
    workspace_id: str
    actor_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    metadata_: Optional[dict] = None

class WorkspaceRepository(BaseRepository[Workspace, WorkspaceInternalCreate, WorkspaceUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Optional[Workspace]:
        query = select(Workspace).where(Workspace.slug == slug)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_workspaces(self, db: AsyncSession, *, user_id: str) -> List[Workspace]:
        query = select(Workspace).join(WorkspaceMember).where(WorkspaceMember.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()

class WorkspaceMemberRepository(BaseRepository[WorkspaceMember, WorkspaceMemberCreate, WorkspaceMemberUpdate]):
    async def get_by_workspace_and_user(self, db: AsyncSession, *, workspace_id: str, user_id: str) -> Optional[WorkspaceMember]:
        query = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        ).options(selectinload(WorkspaceMember.user))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_workspace(self, db: AsyncSession, *, workspace_id: str, skip: int = 0, limit: int = 100) -> List[WorkspaceMember]:
        query = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id
        ).options(selectinload(WorkspaceMember.user)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

class WorkspaceInvitationRepository(BaseRepository[WorkspaceInvitation, WorkspaceInvitationInternalCreate, BaseModel]):
    async def get_by_token(self, db: AsyncSession, *, token: str) -> Optional[WorkspaceInvitation]:
        query = select(WorkspaceInvitation).where(WorkspaceInvitation.token == token)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_workspace(self, db: AsyncSession, *, workspace_id: str, skip: int = 0, limit: int = 100) -> List[WorkspaceInvitation]:
        query = select(WorkspaceInvitation).where(
            WorkspaceInvitation.workspace_id == workspace_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

class WorkspaceAuditRepository(BaseRepository[WorkspaceAuditLog, WorkspaceAuditLogCreate, BaseModel]):
    async def get_multi_by_workspace(self, db: AsyncSession, *, workspace_id: str, skip: int = 0, limit: int = 100) -> List[WorkspaceAuditLog]:
        query = select(WorkspaceAuditLog).where(
            WorkspaceAuditLog.workspace_id == workspace_id
        ).order_by(WorkspaceAuditLog.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

workspace_repo = WorkspaceRepository(Workspace)
workspace_member_repo = WorkspaceMemberRepository(WorkspaceMember)
workspace_invitation_repo = WorkspaceInvitationRepository(WorkspaceInvitation)
workspace_audit_repo = WorkspaceAuditRepository(WorkspaceAuditLog)
