import pytest
from unittest.mock import AsyncMock, patch
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
import uuid

@pytest.fixture
def workspace_service():
    return WorkspaceService()

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def test_user():
    return User(id=uuid.uuid4(), email="owner@test.com", full_name="Owner User")

@pytest.fixture
def test_workspace(test_user):
    return Workspace(id=uuid.uuid4(), name="Test Workspace", slug="test-workspace", owner_id=test_user.id)

@pytest.mark.asyncio
async def test_create_workspace(workspace_service, mock_db, test_user):
    with patch("app.services.workspace_service.workspace_repo") as mock_workspace_repo, \
         patch("app.services.workspace_service.workspace_member_repo") as mock_member_repo, \
         patch("app.services.workspace_service.user_repo") as mock_user_repo, \
         patch("app.services.team_service.TeamService.assign_role", new_callable=AsyncMock) as mock_assign_role, \
         patch("app.services.workspace_service.audit_service") as mock_audit:

        mock_workspace_repo.get_by_slug = AsyncMock(return_value=None)
        
        new_workspace = Workspace(id=uuid.uuid4(), name="Acme Inc", slug="acme-inc", owner_id=test_user.id)
        mock_workspace_repo.create = AsyncMock(return_value=new_workspace)
        mock_member_repo.create = AsyncMock(return_value=WorkspaceMember(id=uuid.uuid4(), workspace_id=new_workspace.id, user_id=test_user.id))
        mock_user_repo.update = AsyncMock()
        mock_audit.log_action = AsyncMock()

        request = WorkspaceCreate(name="Acme Inc", industry="Tech")
        result = await workspace_service.create_workspace(mock_db, test_user, request)

        assert result.name == "Acme Inc"
        mock_member_repo.create.assert_called_once()
        mock_user_repo.update.assert_called_once()
        mock_audit.log_action.assert_called_once()

@pytest.mark.asyncio
async def test_switch_workspace_success(workspace_service, mock_db, test_user, test_workspace):
    with patch("app.services.workspace_service.workspace_member_repo") as mock_member_repo, \
         patch("app.services.workspace_service.workspace_repo") as mock_workspace_repo, \
         patch("app.services.workspace_service.user_repo") as mock_user_repo:

        mock_member_repo.get_by_workspace_and_user = AsyncMock(return_value=WorkspaceMember())
        mock_workspace_repo.get = AsyncMock(return_value=test_workspace)
        mock_user_repo.update = AsyncMock()

        result = await workspace_service.switch_workspace(mock_db, test_user, str(test_workspace.id))
        
        assert result.id == test_workspace.id
        mock_user_repo.update.assert_called_once()

@pytest.mark.asyncio
async def test_switch_workspace_forbidden(workspace_service, mock_db, test_user, test_workspace):
    with patch("app.services.workspace_service.workspace_member_repo") as mock_member_repo:
        mock_member_repo.get_by_workspace_and_user = AsyncMock(return_value=None)

        with pytest.raises(ForbiddenException):
            await workspace_service.switch_workspace(mock_db, test_user, str(test_workspace.id))
