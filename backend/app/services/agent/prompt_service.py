from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from app.repositories.agent_repo import agent_prompt_repo
from app.models.agent import AgentPrompt

class PromptStudioService:
    async def get_prompt(self, db: AsyncSession, agent_id: str) -> Optional[AgentPrompt]:
        return await agent_prompt_repo.get_by_agent(db, agent_id)
        
    async def update_prompt(self, db: AsyncSession, agent_id: str, prompt_data: Dict[str, Any]) -> Optional[AgentPrompt]:
        prompt = await agent_prompt_repo.get_by_agent(db, agent_id)
        if not prompt:
            return None
            
        return await agent_prompt_repo.update(db, db_obj=prompt, obj_in=prompt_data)

prompt_studio_service = PromptStudioService()
