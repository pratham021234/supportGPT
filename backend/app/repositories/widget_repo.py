from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.repositories.base import BaseRepository
from app.models.widget import WidgetConfiguration, WidgetSession
from pydantic import BaseModel

class WidgetConfigurationInternalCreate(BaseModel):
    workspace_id: str
    agent_id: Optional[str] = None
    theme: str = "light"
    primary_color: str = "#000000"
    logo_url: Optional[str] = None
    launcher_text: str = "Chat with us"
    welcome_message: str = "Hello! How can I help you today?"

class WidgetSessionInternalCreate(BaseModel):
    workspace_id: str
    agent_id: Optional[str] = None
    customer_id: Optional[str] = None
    session_token: str

class WidgetConfigurationRepository(BaseRepository[WidgetConfiguration, WidgetConfigurationInternalCreate, BaseModel]):
    async def get_by_agent(self, db: AsyncSession, agent_id: str) -> Optional[WidgetConfiguration]:
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> Optional[WidgetConfiguration]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class WidgetSessionRepository(BaseRepository[WidgetSession, WidgetSessionInternalCreate, BaseModel]):
    async def get_by_token(self, db: AsyncSession, token: str) -> Optional[WidgetSession]:
        query = select(self.model).where(self.model.session_token == token)
        result = await db.execute(query)
        return result.scalar_one_or_none()

widget_config_repo = WidgetConfigurationRepository(WidgetConfiguration)
widget_session_repo = WidgetSessionRepository(WidgetSession)
