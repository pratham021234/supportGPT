from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.models.automation import AutomationRule, WorkflowExecution, WebhookEndpoint, RuleStatus, ExecutionStatus

class AutomationRuleInternalCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    trigger_event: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    status: RuleStatus = RuleStatus.ACTIVE

class WorkflowExecutionInternalCreate(BaseModel):
    workspace_id: str
    rule_id: str
    event_id: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    error_message: Optional[str] = None
    execution_logs: List[Dict[str, Any]] = []

class WebhookEndpointInternalCreate(BaseModel):
    workspace_id: str
    name: str
    url: str
    secret: Optional[str] = None
    is_active: bool = True

class AutomationRuleRepository(BaseRepository[AutomationRule, AutomationRuleInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[AutomationRule]:
        query = select(self.model).where(self.model.workspace_id == workspace_id)
        result = await db.execute(query)
        return list(result.scalars().all())
        
    async def get_active_by_trigger(self, db: AsyncSession, trigger_event: str) -> List[AutomationRule]:
        query = select(self.model).where(
            self.model.trigger_event == trigger_event,
            self.model.status == RuleStatus.ACTIVE
        )
        result = await db.execute(query)
        return list(result.scalars().all())

class WorkflowExecutionRepository(BaseRepository[WorkflowExecution, WorkflowExecutionInternalCreate, BaseModel]):
    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[WorkflowExecution]:
        query = select(self.model).where(self.model.workspace_id == workspace_id).order_by(self.model.executed_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

class WebhookEndpointRepository(BaseRepository[WebhookEndpoint, WebhookEndpointInternalCreate, BaseModel]):
    async def get_active_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[WebhookEndpoint]:
        query = select(self.model).where(
            self.model.workspace_id == workspace_id,
            self.model.is_active == True
        )
        result = await db.execute(query)
        return list(result.scalars().all())

automation_rule_repo = AutomationRuleRepository(AutomationRule)
workflow_execution_repo = WorkflowExecutionRepository(WorkflowExecution)
webhook_endpoint_repo = WebhookEndpointRepository(WebhookEndpoint)
