import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.agent import Agent, AgentStatus
from app.repositories.agent_repo import (
    agent_repo, agent_prompt_repo, agent_model_config_repo, 
    agent_escalation_rule_repo, agent_version_repo,
    AgentVersionInternalCreate, agent_knowledge_scope_repo
)

logger = logging.getLogger(__name__)

class PromptVersionService:
    async def publish_agent_version(self, db: AsyncSession, agent_id: str, user_id: str) -> Optional[Agent]:
        """
        Publishes an agent. Takes a snapshot of current configurations.
        """
        agent = await agent_repo.get(db, id=agent_id)
        if not agent:
            return None
            
        # Fetch current configs
        prompt = await agent_prompt_repo.get_by_agent(db, agent_id)
        model_config = await agent_model_config_repo.get_by_agent(db, agent_id)
        escalation = await agent_escalation_rule_repo.get_by_agent(db, agent_id)
        scopes = await agent_knowledge_scope_repo.get_by_agent(db, agent_id)
        
        # Serialize to JSONB snapshot
        snapshot = {
            "prompt": {
                "system_prompt": prompt.system_prompt if prompt else "",
                "welcome_message": prompt.welcome_message if prompt else "",
                "fallback_message": prompt.fallback_message if prompt else "",
                "tone": prompt.tone if prompt else "",
                "behavior_rules": prompt.behavior_rules if prompt else ""
            },
            "model": {
                "provider": model_config.provider if model_config else "",
                "model": model_config.model if model_config else "",
                "temperature": model_config.temperature if model_config else 0.2,
                "max_tokens": model_config.max_tokens if model_config else 2048
            },
            "escalation": {
                "confidence_threshold": escalation.confidence_threshold if escalation else 70.0,
                "auto_create_ticket": escalation.auto_create_ticket if escalation else False
            },
            "knowledge_scopes": [
                {
                    "document_id": str(s.document_id) if s.document_id else None,
                    "source_id": str(s.source_id) if s.source_id else None,
                    "tag_id": str(s.tag_id) if s.tag_id else None
                } for s in scopes
            ]
        }
        
        # Get next version number
        versions = await agent_version_repo.get_by_agent(db, agent_id)
        next_version = len(versions) + 1
        
        # Save snapshot
        version_in = AgentVersionInternalCreate(
            agent_id=agent_id,
            version_number=next_version,
            configuration_snapshot=snapshot,
            created_by=user_id
        )
        await agent_version_repo.create(db, obj_in=version_in)
        
        # Update status
        return await agent_repo.update(db, db_obj=agent, obj_in={"status": AgentStatus.ACTIVE})
        
    async def restore_version(self, db: AsyncSession, agent_id: str, version_number: int) -> bool:
        """Restores an agent's configuration from a snapshot."""
        versions = await agent_version_repo.get_by_agent(db, agent_id)
        target = next((v for v in versions if v.version_number == version_number), None)
        if not target:
            return False
            
        snap = target.configuration_snapshot
        
        if "prompt" in snap:
            p = await agent_prompt_repo.get_by_agent(db, agent_id)
            if p:
                await agent_prompt_repo.update(db, db_obj=p, obj_in=snap["prompt"])
                
        if "model" in snap:
            m = await agent_model_config_repo.get_by_agent(db, agent_id)
            if m:
                await agent_model_config_repo.update(db, db_obj=m, obj_in=snap["model"])
                
        if "escalation" in snap:
            e = await agent_escalation_rule_repo.get_by_agent(db, agent_id)
            if e:
                await agent_escalation_rule_repo.update(db, db_obj=e, obj_in=snap["escalation"])
                
        # To strictly restore knowledge scopes, we would delete current and insert from snapshot.
        return True

prompt_version_service = PromptVersionService()
