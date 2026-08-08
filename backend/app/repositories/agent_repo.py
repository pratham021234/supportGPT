from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.repositories.base import BaseRepository
from app.models.agent import (
    Agent, AgentPrompt, AgentVersion, AgentKnowledgeScope,
    AgentModelConfig, AgentEscalationRule, AgentStatus, AgentType, AgentVisibility
)
from pydantic import BaseModel

class AgentInternalCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    agent_type: AgentType = AgentType.CUSTOM
    visibility: AgentVisibility = AgentVisibility.INTERNAL
    default_language: str = "en"
    created_by: Optional[str] = None

class AgentPromptInternalCreate(BaseModel):
    agent_id: str
    system_prompt: str
    welcome_message: Optional[str] = None
    fallback_message: Optional[str] = None
    tone: str = "Professional"
    behavior_rules: Optional[str] = None

class AgentModelConfigInternalCreate(BaseModel):
    agent_id: str
    provider: str = "google"
    model: str = "gemini-2.5-flash"
    temperature: float = 0.2
    max_tokens: int = 2048

class AgentEscalationRuleInternalCreate(BaseModel):
    agent_id: str
    confidence_threshold: float = 70.0
    auto_create_ticket: bool = False
    auto_handoff: bool = True
    escalation_message: Optional[str] = "Let me connect you with a human agent who can help."

class AgentVersionInternalCreate(BaseModel):
    agent_id: str
    version_number: int
    configuration_snapshot: Dict[str, Any]
    created_by: Optional[str] = None

class AgentKnowledgeScopeInternalCreate(BaseModel):
    agent_id: str
    document_id: Optional[str] = None
    source_id: Optional[str] = None
    tag_id: Optional[str] = None

class AgentRepository(BaseRepository[Agent, AgentInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[Agent]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())

class AgentPromptRepository(BaseRepository[AgentPrompt, AgentPromptInternalCreate, BaseModel]):
    async def get_by_agent(self, db: AsyncSession, agent_id: str) -> Optional[AgentPrompt]:
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalars().first()

class AgentModelConfigRepository(BaseRepository[AgentModelConfig, AgentModelConfigInternalCreate, BaseModel]):
    async def get_by_agent(self, db: AsyncSession, agent_id: str) -> Optional[AgentModelConfig]:
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalars().first()

class AgentEscalationRuleRepository(BaseRepository[AgentEscalationRule, AgentEscalationRuleInternalCreate, BaseModel]):
    async def get_by_agent(self, db: AsyncSession, agent_id: str) -> Optional[AgentEscalationRule]:
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return result.scalars().first()

class AgentVersionRepository(BaseRepository[AgentVersion, AgentVersionInternalCreate, BaseModel]):
    async def get_by_agent(self, db: AsyncSession, agent_id: str) -> List[AgentVersion]:
        query = select(self.model).where(self.model.agent_id == agent_id).order_by(desc(self.model.version_number))
        result = await db.execute(query)
        return list(result.scalars().all())

class AgentKnowledgeScopeRepository(BaseRepository[AgentKnowledgeScope, AgentKnowledgeScopeInternalCreate, BaseModel]):
    async def get_by_agent(self, db: AsyncSession, agent_id: str) -> List[AgentKnowledgeScope]:
        query = select(self.model).where(self.model.agent_id == agent_id)
        result = await db.execute(query)
        return list(result.scalars().all())

agent_repo = AgentRepository(Agent)
agent_prompt_repo = AgentPromptRepository(AgentPrompt)
agent_model_config_repo = AgentModelConfigRepository(AgentModelConfig)
agent_escalation_rule_repo = AgentEscalationRuleRepository(AgentEscalationRule)
agent_version_repo = AgentVersionRepository(AgentVersion)
agent_knowledge_scope_repo = AgentKnowledgeScopeRepository(AgentKnowledgeScope)
