import pytest
from unittest.mock import AsyncMock, patch
from app.services.team_service import TeamService
from app.models.workspace import WorkspaceMember, Workspace
from app.models.rbac import UserWorkspaceRole, Role
from app.core.exceptions import BadRequestException, ForbiddenException
import uuid

@pytest.fixture
def team_service():
    return TeamService()

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_update_status_prevent_owner_suspension(team_service, mock_db):
    with patch("app.services.team_service.workspace_member_repo") as mock_member_repo, \
         patch("app.services.team_service.user_workspace_role_repo") as mock_uwr_repo:
         
        member = WorkspaceMember(id=uuid.uuid4(), workspace_id=uuid.uuid4(), status="ACTIVE")
        mock_member_repo.get = AsyncMock(return_value=member)
        
        # Mock owner role
        role = Role(name="OWNER")
        u_role = UserWorkspaceRole(role=role)
        mock_uwr_repo.get_by_member = AsyncMock(return_value=[u_role])
        
        with pytest.raises(BadRequestException) as exc:
            await team_service.update_status(mock_db, str(member.workspace_id), str(member.id), "SUSPENDED", str(uuid.uuid4()))
            
        assert "Cannot suspend or remove an OWNER" in str(exc.value.message)

@pytest.mark.asyncio
async def test_transfer_ownership_success(team_service, mock_db):
    with patch("app.services.team_service.workspace_member_repo") as mock_member_repo, \
         patch("app.services.team_service.user_workspace_role_repo") as mock_uwr_repo, \
         patch("app.services.team_service.workspace_repo") as mock_ws_repo, \
         patch.object(team_service, "assign_role", new=AsyncMock()) as mock_assign, \
         patch("app.services.team_service.audit_service") as mock_audit:
         
        current_owner = WorkspaceMember(id=uuid.uuid4(), workspace_id=uuid.uuid4(), status="ACTIVE", user_id=uuid.uuid4())
        new_owner = WorkspaceMember(id=uuid.uuid4(), workspace_id=current_owner.workspace_id, status="ACTIVE", user_id=uuid.uuid4())
        
        mock_member_repo.get = AsyncMock(side_effect=[current_owner, new_owner])
        
        role = Role(name="OWNER")
        u_role = UserWorkspaceRole(role=role)
        mock_uwr_repo.get_by_member = AsyncMock(return_value=[u_role])
        mock_member_repo.update = AsyncMock()
        
        # mock workspace resolution
        mock_ws = Workspace(id=current_owner.workspace_id, owner_id=current_owner.user_id)
        mock_ws_repo.get = AsyncMock(return_value=mock_ws)
        mock_ws_repo.update = AsyncMock()
        
        mock_audit.log_action = AsyncMock()
        
        # Need to mock the workspace relationship resolving correctly or patch the update.
        # Actually it awaits `current_owner.workspace` which is an async relation if lazy loaded.
        result = await team_service.transfer_ownership(mock_db, str(current_owner.workspace_id), str(current_owner.id), str(new_owner.id))
        
        assert result is True
        assert mock_assign.call_count == 2
        # verify new owner got OWNER role, current got ADMIN
        mock_assign.assert_any_call(mock_db, str(new_owner.id), "OWNER", actor_id=str(current_owner.user_id))
        mock_assign.assert_any_call(mock_db, str(current_owner.id), "ADMIN", actor_id=str(current_owner.user_id))
