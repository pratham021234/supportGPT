from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.models.integration import IntegrationConnection, IntegrationSyncLog, ConnectionStatus, SyncStatus

class IntegrationConnectionInternalCreate(BaseModel):
    workspace_id: str
    provider: str
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    config: dict = {}

class IntegrationSyncLogInternalCreate(BaseModel):
    workspace_id: str
    connection_id: str
    provider: str
    resource_type: str
    resource_id: str
    action: str
    status: SyncStatus = SyncStatus.PENDING
    payload_snapshot: Optional[dict] = None

class IntegrationConnectionRepository(BaseRepository[IntegrationConnection, IntegrationConnectionInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[IntegrationConnection]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return list(result.scalars().all())
        
    async def get_active_by_provider(self, db: AsyncSession, workspace_id: str, provider: str) -> Optional[IntegrationConnection]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id,
            self.model.provider == provider,
            self.model.status == ConnectionStatus.CONNECTED
        )
        result = await db.execute(query)
        return result.scalars().first()

class IntegrationSyncLogRepository(BaseRepository[IntegrationSyncLog, IntegrationSyncLogInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str, limit: int = 100) -> List[IntegrationSyncLog]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(self.model.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

integration_conn_repo = IntegrationConnectionRepository(IntegrationConnection)
integration_sync_repo = IntegrationSyncLogRepository(IntegrationSyncLog)
