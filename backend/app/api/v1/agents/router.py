from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from pydantic import BaseModel

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.services.agent.agent_service import agent_service
from app.services.agent.prompt_service import prompt_studio_service
from app.services.agent.testing_service import agent_testing_service
from app.repositories.agent_repo import agent_model_config_repo, agent_escalation_rule_repo, agent_knowledge_scope_repo, AgentKnowledgeScopeInternalCreate

router = APIRouter()

class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: str = "CUSTOM"

class PromptUpdateRequest(BaseModel):
    system_prompt: Optional[str] = None
    welcome_message: Optional[str] = None
    fallback_message: Optional[str] = None
    tone: Optional[str] = None
    behavior_rules: Optional[str] = None

class TestAgentRequest(BaseModel):
    query: str

class RollbackRequest(BaseModel):
    version_number: int

class ModelConfigRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None

class EscalationRuleRequest(BaseModel):
    confidence_threshold: Optional[float] = None
    auto_create_ticket: Optional[bool] = None
    auto_handoff: Optional[bool] = None
    escalation_message: Optional[str] = None

class KnowledgeScopeRequest(BaseModel):
    document_id: Optional[str] = None
    source_id: Optional[str] = None
    tag_id: Optional[str] = None

@router.post("")
async def create_agent(
    req: AgentCreateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new agent with default prompt and configs."""
    agent = await agent_service.create_agent(
        db=db,
        workspace_id=str(member.workspace_id),
        user_id=str(member.user_id),
        agent_data=req.model_dump()
    )
    return agent

@router.get("")
async def list_agents(
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    """Lists all agents in the workspace."""
    agents = await agent_service.get_workspace_agents(db, str(member.workspace_id))
    return agents

@router.post("/{agent_id}/publish")
async def publish_agent(
    agent_id: str,
    member: WorkspaceMember = Depends(require_permission("publish_agents")),
    db: AsyncSession = Depends(get_db)
):
    """Publishes an agent and creates a version snapshot."""
    agent = await agent_service.publish_agent(db, agent_id, str(member.user_id))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/{agent_id}/prompt")
async def update_agent_prompt(
    agent_id: str,
    req: PromptUpdateRequest,
    member: WorkspaceMember = Depends(require_permission("manage_prompts")),
    db: AsyncSession = Depends(get_db)
):
    """Updates the prompt for an agent."""
    prompt = await prompt_studio_service.update_prompt(db, agent_id, req.model_dump(exclude_unset=True))
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.post("/{agent_id}/test")
async def test_agent(
    agent_id: str,
    req: TestAgentRequest,
    member: WorkspaceMember = Depends(require_permission("test_agents")),
    db: AsyncSession = Depends(get_db)
):
    """Tests the agent logic using the workspace RAG Engine."""
    result = await agent_testing_service.test_agent(
        db=db,
        agent_id=agent_id,
        query=req.query,
        user_id=str(member.user_id)
    )
    return result

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    await agent_service.delete_agent(db, agent_id)
    return {"message": "Agent deleted"}

@router.post("/{agent_id}/archive")
async def archive_agent(
    agent_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    agent = await agent_service.archive_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/{agent_id}/clone")
async def clone_agent(
    agent_id: str,
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    agent = await agent_service.clone_agent(db, agent_id, str(member.user_id))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/{agent_id}/rollback")
async def rollback_agent(
    agent_id: str,
    req: RollbackRequest,
    member: WorkspaceMember = Depends(require_permission("publish_agents")),
    db: AsyncSession = Depends(get_db)
):
    success = await agent_service.restore_version(db, agent_id, req.version_number)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"message": "Rollback successful"}

@router.patch("/{agent_id}/model")
async def update_model_config(
    agent_id: str,
    req: ModelConfigRequest,
    member: WorkspaceMember = Depends(require_permission("manage_prompts")),
    db: AsyncSession = Depends(get_db)
):
    model_config = await agent_model_config_repo.get_by_agent(db, agent_id)
    if not model_config:
        raise HTTPException(404, "Agent not found")
    return await agent_model_config_repo.update(db, db_obj=model_config, obj_in=req.model_dump(exclude_unset=True))

@router.patch("/{agent_id}/escalation")
async def update_escalation_rules(
    agent_id: str,
    req: EscalationRuleRequest,
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    esc = await agent_escalation_rule_repo.get_by_agent(db, agent_id)
    if not esc:
        raise HTTPException(404, "Agent not found")
    return await agent_escalation_rule_repo.update(db, db_obj=esc, obj_in=req.model_dump(exclude_unset=True))

@router.post("/{agent_id}/knowledge")
async def assign_knowledge(
    agent_id: str,
    req: KnowledgeScopeRequest,
    member: WorkspaceMember = Depends(require_permission("manage_agents")),
    db: AsyncSession = Depends(get_db)
):
    scope_in = AgentKnowledgeScopeInternalCreate(
        agent_id=agent_id,
        document_id=req.document_id,
        source_id=req.source_id,
        tag_id=req.tag_id
    )
    return await agent_knowledge_scope_repo.create(db, obj_in=scope_in)

@router.get("/{agent_id}/analytics")
async def get_agent_analytics(
    agent_id: str,
    member: WorkspaceMember = Depends(require_permission("view_agents")),
    db: AsyncSession = Depends(get_db)
):
    # Mocking analytics data for MVP
    return {
        "questions_answered": 1420,
        "resolution_rate": 87.5,
        "escalation_rate": 12.5,
        "average_confidence": 92.1,
        "avg_response_time_ms": 1240,
        "customer_satisfaction": 4.8
    }
