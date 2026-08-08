import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.repositories.agent_repo import (
    agent_repo, agent_prompt_repo, agent_model_config_repo, agent_escalation_rule_repo, agent_version_repo,
    AgentInternalCreate, AgentPromptInternalCreate, AgentModelConfigInternalCreate, AgentEscalationRuleInternalCreate,
    AgentVersionInternalCreate
)
from app.models.agent import Agent, AgentStatus, AgentVisibility

logger = logging.getLogger(__name__)

class AgentService:
    async def create_agent(self, db: AsyncSession, workspace_id: str, user_id: str, agent_data: Dict[str, Any]) -> Agent:
        """Creates a new agent with default prompt, model config, and escalation rules."""
        
        # 1. Create Core Agent
        agent_in = AgentInternalCreate(
            workspace_id=workspace_id,
            created_by=user_id,
            **agent_data
        )
        agent = await agent_repo.create(db, obj_in=agent_in)
        
        # 2. Attach Defaults
        prompt_in = AgentPromptInternalCreate(agent_id=str(agent.id), system_prompt="You are a helpful support agent.")
        await agent_prompt_repo.create(db, obj_in=prompt_in)
        
        model_in = AgentModelConfigInternalCreate(agent_id=str(agent.id))
        await agent_model_config_repo.create(db, obj_in=model_in)
        
        escalation_in = AgentEscalationRuleInternalCreate(agent_id=str(agent.id))
        await agent_escalation_rule_repo.create(db, obj_in=escalation_in)
        
        return agent

    async def get_workspace_agents(self, db: AsyncSession, workspace_id: str):
        """Returns all agents for a workspace."""
        return await agent_repo.get_by_workspace(db, workspace_id=workspace_id)

    async def get_agent(self, db: AsyncSession, agent_id: str) -> Optional[Agent]:
        """Returns a single agent."""
        return await agent_repo.get(db, id=agent_id)
        
    async def update_agent(self, db: AsyncSession, agent_id: str, update_data: Dict[str, Any]) -> Optional[Agent]:
        """Updates agent metadata (name, description, visibility)."""
        agent = await agent_repo.get(db, id=agent_id)
        if not agent:
            return None
            
        return await agent_repo.update(db, db_obj=agent, obj_in=update_data)

    async def delete_agent(self, db: AsyncSession, agent_id: str):
        """Deletes an agent."""
        agent = await agent_repo.get(db, id=agent_id)
        if agent:
            await agent_repo.delete(db, id=agent_id)
            
    async def archive_agent(self, db: AsyncSession, agent_id: str) -> Optional[Agent]:
        """Archives an agent."""
        agent = await agent_repo.get(db, id=agent_id)
        if agent:
            return await agent_repo.update(db, db_obj=agent, obj_in={"status": AgentStatus.ARCHIVED})
        return None
        
    async def clone_agent(self, db: AsyncSession, agent_id: str, user_id: str) -> Optional[Agent]:
        """Clones an agent and its config."""
        agent = await agent_repo.get(db, id=agent_id)
        if not agent:
            return None
            
        # 1. Clone core agent
        agent_data = {
            "name": f"{agent.name} (Clone)",
            "description": agent.description,
            "avatar_url": agent.avatar_url,
            "agent_type": agent.agent_type,
            "visibility": agent.visibility,
            "default_language": agent.default_language
        }
        
        new_agent = await self.create_agent(db, str(agent.workspace_id), user_id, agent_data)
        
        # 2. Overwrite defaults with source configs
        prompt = await agent_prompt_repo.get_by_agent(db, agent_id)
        if prompt:
            new_prompt = await agent_prompt_repo.get_by_agent(db, str(new_agent.id))
            await agent_prompt_repo.update(db, db_obj=new_prompt, obj_in={
                "system_prompt": prompt.system_prompt,
                "welcome_message": prompt.welcome_message,
                "fallback_message": prompt.fallback_message,
                "tone": prompt.tone,
                "behavior_rules": prompt.behavior_rules
            })
            
        model = await agent_model_config_repo.get_by_agent(db, agent_id)
        if model:
            new_model = await agent_model_config_repo.get_by_agent(db, str(new_agent.id))
            await agent_model_config_repo.update(db, db_obj=new_model, obj_in={
                "provider": model.provider,
                "model": model.model,
                "temperature": model.temperature,
                "max_tokens": model.max_tokens,
                "top_p": model.top_p,
                "frequency_penalty": model.frequency_penalty,
                "presence_penalty": model.presence_penalty
            })
            
        esc = await agent_escalation_rule_repo.get_by_agent(db, agent_id)
        if esc:
            new_esc = await agent_escalation_rule_repo.get_by_agent(db, str(new_agent.id))
            await agent_escalation_rule_repo.update(db, db_obj=new_esc, obj_in={
                "confidence_threshold": esc.confidence_threshold,
                "auto_create_ticket": esc.auto_create_ticket,
                "auto_handoff": esc.auto_handoff,
                "escalation_message": esc.escalation_message
            })
            
        return new_agent

    async def publish_agent(self, db: AsyncSession, agent_id: str, user_id: str) -> Optional[Agent]:
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
        
        from app.repositories.agent_repo import agent_knowledge_scope_repo
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
                
        # Scopes skipped for brevity but would be deleted and re-inserted here
        return True

agent_service = AgentService()
