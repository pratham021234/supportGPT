from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import (
    workspace_member_repo, user_workspace_role_repo, role_repo, user_repo, workspace_repo
)
from app.repositories.rbac_repo import UserWorkspaceRoleCreate
from app.models.workspace import WorkspaceMember
from app.models.rbac import UserWorkspaceRole
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.services.audit_service import audit_service
from app.services.permission_service import permission_service

class TeamService:
    async def get_members(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[WorkspaceMember]:
        return await workspace_member_repo.get_multi_by_workspace(db, workspace_id=workspace_id, skip=skip, limit=limit)

    async def get_member(self, db: AsyncSession, workspace_id: str, member_id: str) -> WorkspaceMember:
        member = await workspace_member_repo.get(db, id=member_id)
        if not member or str(member.workspace_id) != workspace_id:
            raise NotFoundException("Member not found in this workspace")
        return member

    async def assign_role(self, db: AsyncSession, workspace_member_id: str, role_name: str, actor_id: str = None) -> UserWorkspaceRole:
        """
        Assigns a role by name to a workspace member. Removes existing roles for simplicity in this implementation.
        """
        member = await workspace_member_repo.get(db, id=workspace_member_id)
        if not member:
            raise NotFoundException("Member not found")
            
        # Find the role (system role or custom role for this workspace)
        role = await role_repo.get_by_name_and_workspace(db, name=role_name, workspace_id=str(member.workspace_id))
        if not role:
            # Fallback to check if it's a pure system role
            roles = await role_repo.get_system_roles(db)
            role = next((r for r in roles if r.name == role_name), None)
            if not role:
                raise NotFoundException(f"Role '{role_name}' not found")

        # Delete existing roles to prevent multi-role confusion unless we strictly want multiple
        await user_workspace_role_role_delete(db, workspace_member_id)
        
        assignment_in = UserWorkspaceRoleCreate(
            workspace_member_id=workspace_member_id,
            role_id=str(role.id),
            assigned_by=actor_id
        )
        assignment = await user_workspace_role_repo.create(db, obj_in=assignment_in)
        
        # Invalidate cache
        await permission_service.invalidate_member_cache(workspace_member_id)
        
        return assignment
        
    async def assign_role_by_id(self, db: AsyncSession, workspace_id: str, member_id: str, role_id: str, actor_id: str) -> UserWorkspaceRole:
        member = await self.get_member(db, workspace_id, member_id)
        role = await role_repo.get(db, id=role_id)
        
        if not role or (role.workspace_id and str(role.workspace_id) != workspace_id):
            raise NotFoundException("Role not found or not applicable to this workspace")
            
        await user_workspace_role_role_delete(db, member_id)
        
        assignment_in = UserWorkspaceRoleCreate(
            workspace_member_id=member_id,
            role_id=role_id,
            assigned_by=actor_id
        )
        assignment = await user_workspace_role_repo.create(db, obj_in=assignment_in)
        
        await permission_service.invalidate_member_cache(member_id)
        
        await audit_service.log_action(
            db, workspace_id=workspace_id, action="ROLE_ASSIGNED",
            resource_type="workspace_member", actor_id=actor_id, resource_id=member_id,
            metadata_={"role_id": role_id, "role_name": role.name}
        )
        
        return assignment

    async def update_status(self, db: AsyncSession, workspace_id: str, member_id: str, status: str, actor_id: str) -> WorkspaceMember:
        if status not in ["ACTIVE", "SUSPENDED", "REMOVED"]:
            raise BadRequestException("Invalid status")
            
        member = await self.get_member(db, workspace_id, member_id)
        
        # Prevent suspending/removing the owner
        roles = await user_workspace_role_repo.get_by_member(db, member_id)
        is_owner = any(r.role and r.role.name == "OWNER" for r in roles)
        
        if is_owner and status != "ACTIVE":
            raise BadRequestException("Cannot suspend or remove an OWNER. Transfer ownership first.")
            
        updated_member = await workspace_member_repo.update(db, db_obj=member, obj_in={"status": status})
        
        # Invalidate cache if suspended
        await permission_service.invalidate_member_cache(member_id)
        
        await audit_service.log_action(
            db, workspace_id=workspace_id, action=f"MEMBER_{status}",
            resource_type="workspace_member", actor_id=actor_id, resource_id=member_id
        )
        
        return updated_member

    async def transfer_ownership(self, db: AsyncSession, workspace_id: str, current_owner_member_id: str, new_owner_member_id: str) -> bool:
        current_owner = await self.get_member(db, workspace_id, current_owner_member_id)
        new_owner = await self.get_member(db, workspace_id, new_owner_member_id)
        
        if new_owner.status != "ACTIVE":
            raise BadRequestException("New owner must be an ACTIVE member")
            
        # Verify current owner has OWNER role
        current_roles = await user_workspace_role_repo.get_by_member(db, current_owner_member_id)
        if not any(r.role and r.role.name == "OWNER" for r in current_roles):
            raise ForbiddenException("You are not the OWNER of this workspace")
            
        # Assign OWNER to new member
        await self.assign_role(db, new_owner_member_id, "OWNER", actor_id=str(current_owner.user_id))
        
        # Demote current owner to ADMIN
        await self.assign_role(db, current_owner_member_id, "ADMIN", actor_id=str(current_owner.user_id))
        
        # Also update workspace owner_id
        workspace = await workspace_repo.get(db, id=workspace_id)
        if workspace:
            await workspace_repo.update(db, db_obj=workspace, obj_in={"owner_id": str(new_owner.user_id)})
        
        await audit_service.log_action(
            db, workspace_id=workspace_id, action="OWNERSHIP_TRANSFERRED",
            resource_type="workspace", actor_id=str(current_owner.user_id),
            metadata_={"old_owner_id": current_owner_member_id, "new_owner_id": new_owner_member_id}
        )
        
        return True

async def user_workspace_role_role_delete(db: AsyncSession, member_id: str):
    await user_workspace_role_repo.delete_by_member(db, member_id)

team_service = TeamService()
