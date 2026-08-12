import re
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import workspace_repo, workspace_member_repo, user_repo
from app.repositories.workspace_repo import WorkspaceInternalCreate, WorkspaceMemberCreate
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.models.workspace import Workspace, WorkspaceMember
from app.models.user import User
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.services.audit_service import audit_service

def generate_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

class WorkspaceService:
    async def create_workspace(self, db: AsyncSession, user: User, data: WorkspaceCreate) -> Workspace:
        base_slug = generate_slug(data.name)
        if not base_slug:
            base_slug = "workspace"
            
        # Ensure slug uniqueness
        slug = base_slug
        counter = 1
        while await workspace_repo.get_by_slug(db, slug=slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        workspace_in = WorkspaceInternalCreate(
            name=data.name,
            slug=slug,
            description=data.description,
            logo_url=data.logo_url,
            industry=data.industry,
            website=data.website,
            owner_id=str(user.id)
        )

        workspace = await workspace_repo.create(db, obj_in=workspace_in)
        
        # Add creator as ACTIVE member
        member_in = WorkspaceMemberCreate(
            workspace_id=str(workspace.id),
            user_id=str(user.id),
            status="ACTIVE"
        )
        member = await workspace_member_repo.create(db, obj_in=member_in)
        
        # Assign OWNER role
        from app.services.team_service import team_service
        await team_service.assign_role(db, str(member.id), "OWNER", actor_id=str(user.id))

        # Automatically switch user to this workspace
        await user_repo.update(db, db_obj=user, obj_in={"active_workspace_id": str(workspace.id)})

        await audit_service.log_action(
            db, workspace_id=str(workspace.id), action="WORKSPACE_CREATED",
            resource_type="workspace", actor_id=str(user.id), resource_id=str(workspace.id)
        )

        return workspace

    async def get_user_workspaces(self, db: AsyncSession, user_id: str) -> List[Workspace]:
        return await workspace_repo.get_user_workspaces(db, user_id=user_id)

    async def switch_workspace(self, db: AsyncSession, user: User, workspace_id: str) -> Workspace:
        member = await workspace_member_repo.get_by_workspace_and_user(db, workspace_id=workspace_id, user_id=str(user.id))
        if not member:
            raise ForbiddenException("You are not a member of this workspace")
            
        workspace = await workspace_repo.get(db, id=workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
            
        await user_repo.update(db, db_obj=user, obj_in={"active_workspace_id": workspace_id})
        return workspace

    async def update_settings(self, db: AsyncSession, workspace_id: str, data: WorkspaceUpdate, actor_id: str) -> Workspace:
        workspace = await workspace_repo.get(db, id=workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
            
        updated_workspace = await workspace_repo.update(db, db_obj=workspace, obj_in=data)
        
        await audit_service.log_action(
            db, workspace_id=workspace_id, action="SETTINGS_UPDATED",
            resource_type="workspace", actor_id=actor_id, metadata_=data.model_dump(exclude_unset=True)
        )
        
        return updated_workspace

    async def get_workspace(self, db: AsyncSession, workspace_id: str, user_id: str) -> Workspace:
        workspace = await workspace_repo.get(db, id=workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        # Optional: check if user is member
        member = await workspace_member_repo.get_by_workspace_and_user(db, workspace_id=workspace_id, user_id=user_id)
        if not member:
            raise ForbiddenException("You do not have access to this workspace")
        return workspace

    async def delete_workspace(self, db: AsyncSession, workspace_id: str, actor_id: str) -> bool:
        workspace = await workspace_repo.get(db, id=workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
            
        # Delete related members? Usually cascade delete handles this, or soft delete.
        await workspace_repo.delete(db, id=workspace_id)
        
        await audit_service.log_action(
            db, workspace_id=workspace_id, action="WORKSPACE_DELETED",
            resource_type="workspace", actor_id=actor_id, resource_id=workspace_id
        )
        return True

workspace_service = WorkspaceService()
