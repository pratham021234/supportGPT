import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent, AgentStatus
from app.repositories.agent_repo import agent_repo
from app.services.agent.agent_performance_service import agent_performance_service

logger = logging.getLogger(__name__)

class AgentHealthService:
    async def check_health(self, db: AsyncSession, agent_id: str) -> Dict[str, Any]:
        """
        Monitors an agent's health including status, confidence anomalies, and latency.
        """
        agent = await agent_repo.get(db, id=agent_id)
        if not agent:
            return {"status": "NOT_FOUND"}
            
        metrics = await agent_performance_service.get_agent_metrics(db, agent_id)
        
        health_status = "HEALTHY"
        issues = []
        
        if agent.status != AgentStatus.ACTIVE:
            health_status = "WARNING"
            issues.append(f"Agent is in {agent.status.value} state, not ACTIVE.")
            
        if metrics["average_confidence"] > 0 and metrics["average_confidence"] < 70.0:
            health_status = "DEGRADED"
            issues.append(f"Low average confidence: {metrics['average_confidence']}%")
            
        if metrics["escalation_rate"] > 20.0:
            health_status = "DEGRADED"
            issues.append(f"High escalation rate: {metrics['escalation_rate']}%")
            
        return {
            "agent_id": str(agent.id),
            "health": health_status,
            "issues": issues,
            "metrics": metrics
        }

agent_health_service = AgentHealthService()
