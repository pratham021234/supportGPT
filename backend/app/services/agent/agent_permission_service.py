import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent import Agent, AgentVisibility
from app.models.workspace import WorkspaceMember

logger = logging.getLogger(__name__)

class AgentPermissionService:
    def can_invoke_agent(self, agent: Agent, member: WorkspaceMember) -> bool:
        """
        Checks if the requesting member has permission to invoke or talk to the agent.
        """
        if agent.visibility == AgentVisibility.PUBLIC:
            return True
            
        if agent.visibility == AgentVisibility.INTERNAL:
            return str(agent.workspace_id) == str(member.workspace_id)
            
        if agent.visibility == AgentVisibility.PRIVATE:
            return str(agent.created_by) == str(member.user_id)
            
        return False
        
    def can_manage_agent(self, agent: Agent, member: WorkspaceMember) -> bool:
        """
        Checks if the requesting member can edit the agent's prompts or configs.
        Requires workspace admin/owner role, or being the creator.
        """
        if str(agent.created_by) == str(member.user_id):
            return True
            
        if member.role in ["OWNER", "ADMIN"] and str(agent.workspace_id) == str(member.workspace_id):
            return True
            
        return False

agent_permission_service = AgentPermissionService()
