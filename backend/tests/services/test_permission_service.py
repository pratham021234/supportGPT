import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.permission_service import PermissionService
from app.models.rbac import UserWorkspaceRole, Role, RolePermission, Permission

@pytest.fixture
def permission_service():
    return PermissionService()

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_member_permissions_cache_hit(permission_service, mock_db):
    with patch("app.services.permission_service.redis_client") as mock_redis:
        mock_redis.get = AsyncMock(return_value=json.dumps(["manage_team", "view_documents"]))
        
        perms = await permission_service.get_member_permissions(mock_db, "member-123")
        
        assert "manage_team" in perms
        assert "view_documents" in perms
        assert len(perms) == 2

@pytest.mark.asyncio
async def test_get_member_permissions_cache_miss(permission_service, mock_db):
    with patch("app.services.permission_service.redis_client") as mock_redis, \
         patch("app.services.permission_service.user_workspace_role_repo") as mock_uwr_repo:
         
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()
        
        # Mocking DB structure
        perm1 = Permission(name="manage_agents")
        perm2 = Permission(name="create_agent")
        
        role_perm1 = RolePermission(permission=perm1)
        role_perm2 = RolePermission(permission=perm2)
        
        role = Role(permissions=[role_perm1, role_perm2])
        u_role = UserWorkspaceRole(role=role)
        
        mock_uwr_repo.get_by_member = AsyncMock(return_value=[u_role])
        
        perms = await permission_service.get_member_permissions(mock_db, "member-123")
        
        assert "manage_agents" in perms
        assert "create_agent" in perms
        assert len(perms) == 2
        mock_redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_has_permission(permission_service, mock_db):
    with patch.object(permission_service, "get_member_permissions", return_value={"manage_billing", "view_analytics"}):
        assert await permission_service.has_permission(mock_db, "member-123", "manage_billing") is True
        assert await permission_service.has_permission(mock_db, "member-123", "delete_agent") is False
