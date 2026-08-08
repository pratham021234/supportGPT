from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.models.security import ApiKey, SecurityAlert, AlertSeverity

class ApiKeyInternalCreate(BaseModel):
    workspace_id: str
    user_id: str
    name: str
    key_hash: str
    prefix: str
    scopes: List[str] = []

class SecurityAlertInternalCreate(BaseModel):
    workspace_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    metadata_: Optional[dict] = None

class ApiKeyRepository(BaseRepository[ApiKey, ApiKeyInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[ApiKey]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

class SecurityAlertRepository(BaseRepository[SecurityAlert, SecurityAlertInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[SecurityAlert]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

api_key_repo = ApiKeyRepository(ApiKey)
security_alert_repo = SecurityAlertRepository(SecurityAlert)
