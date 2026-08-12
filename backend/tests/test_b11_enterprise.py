import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
import uuid

from app.services.organization_service import (
    workspace_management_service,
    invitation_service,
    audit_log_service,
    role_service
)

@pytest.mark.asyncio
async def test_workspace_creation_with_org(db_session: AsyncSession):
    with patch("sqlalchemy.ext.asyncio.AsyncSession.add") as mock_add, patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new_callable=AsyncMock):
        org_id = str(uuid.uuid4())
        owner_id = str(uuid.uuid4())
        ws = await workspace_management_service.create_workspace(
            db_session, org_id, owner_id, {"name": "Test", "slug": "test-ws"}
        )
        assert ws.name == "Test"
        assert str(ws.organization_id) == org_id
        mock_add.assert_called_once()

@pytest.mark.asyncio
async def test_invitation_service(db_session: AsyncSession):
    with patch("sqlalchemy.ext.asyncio.AsyncSession.add") as mock_add, patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new_callable=AsyncMock):
        ws_id = str(uuid.uuid4())
        inviter_id = str(uuid.uuid4())
        invite = await invitation_service.invite_member(
            db_session, ws_id, inviter_id, "test@example.com", "Admin"
        )
        assert invite.email == "test@example.com"
        assert invite.role == "Admin"
        assert invite.token is not None
        mock_add.assert_called_once()
        
@pytest.mark.asyncio
async def test_audit_log_service(db_session: AsyncSession):
    with patch("sqlalchemy.ext.asyncio.AsyncSession.add") as mock_add, patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new_callable=AsyncMock):
        ws_id = str(uuid.uuid4())
        actor_id = str(uuid.uuid4())
        await audit_log_service.log_action(
            db_session, ws_id, actor_id, "UPDATED_ROLES", "USER"
        )
        mock_add.assert_called_once()

@pytest.mark.asyncio
async def test_role_service(db_session: AsyncSession):
    with patch("sqlalchemy.ext.asyncio.AsyncSession.add") as mock_add, patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new_callable=AsyncMock):
        ws_id = str(uuid.uuid4())
        await role_service.create_default_roles(db_session, ws_id)
        assert mock_add.call_count == 5
