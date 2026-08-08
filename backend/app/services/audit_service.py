from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
from app.repositories import workspace_audit_repo
from app.repositories.workspace_repo import WorkspaceAuditLogCreate

class AuditLogService:
    async def log_action(
        self,
        db: AsyncSession,
        workspace_id: str,
        action: str,
        resource_type: str,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata_: Optional[dict] = None
    ) -> None:
        """
        Record an action in the workspace audit log.
        """
        audit_in = WorkspaceAuditLogCreate(
            workspace_id=workspace_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_=metadata_
        )
        await workspace_audit_repo.create(db, obj_in=audit_in)

    async def get_workspace_logs(self, db: AsyncSession, workspace_id: str, skip: int = 0, limit: int = 100):
        return await workspace_audit_repo.get_multi_by_workspace(db, workspace_id=workspace_id, skip=skip, limit=limit)

audit_service = AuditLogService()
