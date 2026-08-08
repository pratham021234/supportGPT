import secrets
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import workspace_invitation_repo, workspace_member_repo, user_repo
from app.repositories.workspace_repo import WorkspaceInvitationInternalCreate, WorkspaceMemberCreate
from app.schemas.workspace import WorkspaceInvitationCreate
from app.models.workspace import WorkspaceInvitation
from app.core.exceptions import BadRequestException, NotFoundException
from app.services.email_service import email_service
from app.services.audit_service import audit_service

class InvitationService:
    async def invite_member(self, db: AsyncSession, workspace_id: str, data: WorkspaceInvitationCreate, actor_id: str) -> WorkspaceInvitation:
        if data.role not in ["ADMIN", "SUPPORT_AGENT"]:
            raise BadRequestException("Can only invite as ADMIN or SUPPORT_AGENT")
            
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        invitation_in = WorkspaceInvitationInternalCreate(
            email=data.email,
            role=data.role,
            workspace_id=workspace_id,
            token=token,
            expires_at=expires_at.isoformat(),
            invited_by=actor_id
        )
        
        invitation = await workspace_invitation_repo.create(db, obj_in=invitation_in)
        
        # In a real app, you'd send an email here using the email_service
        subject = "You've been invited to a SupportGPT Workspace"
        html = f"<p>You've been invited to join a workspace as {data.role}. Click here to accept: /workspaces/accept?token={token}</p>"
        await email_service.send_email(data.email, subject, html)
        
        await audit_service.log_action(
            db, workspace_id=workspace_id, action="MEMBER_INVITED",
            resource_type="workspace_invitation", actor_id=actor_id, resource_id=str(invitation.id),
            metadata_={"email": data.email, "role": data.role}
        )
        
        return invitation

    async def get_invitations(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100) -> List[WorkspaceInvitation]:
        return await workspace_invitation_repo.get_multi_by_workspace(db, workspace_id=workspace_id, skip=skip, limit=limit)

    async def accept_invitation(self, db: AsyncSession, user_id: str, token: str) -> bool:
        invitation = await workspace_invitation_repo.get_by_token(db, token=token)
        
        if not invitation:
            raise BadRequestException("Invalid or expired invitation token")
            
        if invitation.accepted:
            raise BadRequestException("Invitation already accepted")
            
        if invitation.expires_at.replace(tzinfo=None) < datetime.utcnow():
            raise BadRequestException("Invitation expired")
            
        user = await user_repo.get(db, id=user_id)
        if not user or user.email != invitation.email:
            raise BadRequestException("This invitation is not for your email address")
            
        # Check if already a member
        existing_member = await workspace_member_repo.get_by_workspace_and_user(
            db, workspace_id=str(invitation.workspace_id), user_id=user_id
        )
        if existing_member:
            raise BadRequestException("You are already a member of this workspace")
            
        # Create membership
        member_in = WorkspaceMemberCreate(
            workspace_id=str(invitation.workspace_id),
            user_id=user_id,
            status="ACTIVE"
        )
        member = await workspace_member_repo.create(db, obj_in=member_in)
        
        # Assign role
        from app.services.team_service import team_service
        await team_service.assign_role(db, str(member.id), invitation.role, actor_id=user_id)
        
        # Mark invitation as accepted
        await workspace_invitation_repo.update(db, db_obj=invitation, obj_in={"accepted": True})
        
        # Set as active workspace if none
        if not user.active_workspace_id:
            await user_repo.update(db, db_obj=user, obj_in={"active_workspace_id": str(invitation.workspace_id)})
            
        await audit_service.log_action(
            db, workspace_id=str(invitation.workspace_id), action="INVITATION_ACCEPTED",
            resource_type="workspace_member", actor_id=user_id, resource_id=str(invitation.id)
        )
        
        return True

invitation_service = InvitationService()
