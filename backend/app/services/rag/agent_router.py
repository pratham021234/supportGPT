import logging

logger = logging.getLogger(__name__)

class AgentRouter:
    def determine_agent(self, intent: str, query: str) -> str:
        """
        Determines the agent routing based on intent.
        Fallback to SUPPORT.
        """
        intent = intent.upper()
        if intent == "SALES":
            return "SALES"
        elif intent == "HR":
            return "HR"
        elif intent in ["TROUBLESHOOTING", "TECHNICAL"]:
            return "TECHNICAL"
        else:
            return "SUPPORT"

agent_router = AgentRouter()
