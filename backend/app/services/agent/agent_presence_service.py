import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.repositories.handoff_repo import (
    presence_repo, AgentPresence, AgentPresenceStatus, AgentPresenceInternalCreate
)

logger = logging.getLogger(__name__)

class AgentPresenceService:
    async def get_presence(self, db: AsyncSession, workspace_id: str, user_id: str) -> AgentPresence:
        presence = await presence_repo.get_by_user(db, workspace_id, user_id)
        if not presence:
            presence_in = AgentPresenceInternalCreate(
                workspace_id=workspace_id,
                user_id=user_id,
                current_status=AgentPresenceStatus.ONLINE,
                active_conversations=0
            )
            presence = await presence_repo.create(db, obj_in=presence_in)
        return presence

    async def update_status(self, db: AsyncSession, workspace_id: str, user_id: str, status: AgentPresenceStatus) -> AgentPresence:
        presence = await self.get_presence(db, workspace_id, user_id)
        return await presence_repo.update(db, db_obj=presence, obj_in={"current_status": status})

    async def get_available_agents(self, db: AsyncSession, workspace_id: str) -> List[AgentPresence]:
        """Returns all agents that are ONLINE and have capacity."""
        all_presence = await presence_repo.get_workspace_presence(db, workspace_id)
        # simplistic capacity check: active < 5
        return [p for p in all_presence if p.current_status == AgentPresenceStatus.ONLINE and p.active_conversations < 5]

    async def increment_active_conversations(self, db: AsyncSession, workspace_id: str, user_id: str):
        presence = await self.get_presence(db, workspace_id, user_id)
        await presence_repo.update(db, db_obj=presence, obj_in={"active_conversations": presence.active_conversations + 1})
        
    async def decrement_active_conversations(self, db: AsyncSession, workspace_id: str, user_id: str):
        presence = await self.get_presence(db, workspace_id, user_id)
        if presence.active_conversations > 0:
            await presence_repo.update(db, db_obj=presence, obj_in={"active_conversations": presence.active_conversations - 1})

agent_presence_service = AgentPresenceService()
