import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
import json

from app.models.agent import Agent, AgentStatus
from app.repositories.agent_repo import agent_repo
from app.core.config import settings

logger = logging.getLogger(__name__)

class MultiAgentRouter:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    async def route_query(self, db: AsyncSession, workspace_id: str, query: str) -> Optional[Agent]:
        """
        Evaluates the inbound query against all active agents in the workspace
        and determines the most appropriate agent to handle it.
        """
        agents = await agent_repo.get_by_workspace(db, workspace_id)
        active_agents = [a for a in agents if a.status == AgentStatus.ACTIVE]
        
        if not active_agents:
            # Fallback to drafting/default agent if no active ones exist
            return agents[0] if agents else None
            
        if len(active_agents) == 1:
            return active_agents[0]
            
        if not self.model:
            logger.warning("AgentRouter: GEMINI_API_KEY not set, falling back to first active agent.")
            return active_agents[0]
            
        # Build prompt for routing
        agent_descriptions = "\n".join([f"- ID: {a.id}, Name: {a.name}, Description: {a.description}, Type: {a.agent_type.value}" for a in active_agents])
        
        prompt = f"""
        You are an intelligent routing engine. Your job is to assign a customer query to the most appropriate AI agent.
        
        Customer Query:
        "{query}"
        
        Available Agents:
        {agent_descriptions}
        
        Analyze the query and determine the best agent ID to handle it.
        Return ONLY a JSON object with the key "agent_id".
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up potential markdown formatting from LLM
            content = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            
            selected_id = result.get("agent_id")
            selected_agent = next((a for a in active_agents if str(a.id) == selected_id), None)
            
            if selected_agent:
                return selected_agent
        except Exception as e:
            logger.error(f"AgentRouter LLM error: {e}")
            
        # Fallback to the first available
        return active_agents[0]

multi_agent_router = MultiAgentRouter()
