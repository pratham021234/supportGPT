import json
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import user_workspace_role_repo, role_repo
from app.dependencies.rate_limit import redis_client

class PermissionService:
    async def get_member_permissions(self, db: AsyncSession, workspace_member_id: str) -> Set[str]:
        """
        Calculates and returns the flattened set of permissions for a workspace member.
        Attempts to read from Redis cache first.
        """
        cache_key = f"member_perms:{workspace_member_id}"
        
        # Try Cache
        if redis_client:
            cached_perms = await redis_client.get(cache_key)
            if cached_perms:
                return set(json.loads(cached_perms))
                
        # Resolve from DB
        roles = await user_workspace_role_repo.get_by_member(db, workspace_member_id)
        
        permissions = set()
        for u_role in roles:
            if not u_role.role:
                continue
            for r_perm in u_role.role.permissions:
                if not r_perm.permission:
                    continue
                permissions.add(r_perm.permission.name)
                
        # Store in Cache for 1 hour
        if redis_client:
            await redis_client.set(cache_key, json.dumps(list(permissions)), ex=3600)
            
        return permissions

    async def has_permission(self, db: AsyncSession, workspace_member_id: str, permission_name: str) -> bool:
        """
        Checks if a member has a specific permission.
        """
        perms = await self.get_member_permissions(db, workspace_member_id)
        return permission_name in perms

    async def invalidate_member_cache(self, workspace_member_id: str):
        """
        Invalidates the permission cache for a specific member.
        Called when roles are reassigned.
        """
        if redis_client:
            cache_key = f"member_perms:{workspace_member_id}"
            await redis_client.delete(cache_key)
            
    async def get_role_permissions(self, db: AsyncSession, role_id: str) -> List[str]:
        role = await role_repo.get_with_permissions(db, role_id)
        if not role:
            return []
        return [rp.permission.name for rp in role.permissions]

permission_service = PermissionService()
