import logging
from typing import Dict, Any
from app.services.integrations.base import BaseConnector
import uuid

logger = logging.getLogger(__name__)

class MockConnector(BaseConnector):
    """A generic mock connector to simulate OAuth and API pushes for the MVP."""
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        
    async def connect(self, workspace_id: str, auth_code: str) -> dict:
        logger.info(f"[{self.provider_name}] Connecting workspace {workspace_id} with code {auth_code}")
        # Return mock tokens
        return {
            "access_token": f"mock_access_{uuid.uuid4().hex[:8]}",
            "refresh_token": f"mock_refresh_{uuid.uuid4().hex[:8]}"
        }
        
    async def disconnect(self, workspace_id: str):
        logger.info(f"[{self.provider_name}] Disconnecting workspace {workspace_id}")
        
    async def push_data(self, workspace_id: str, resource_type: str, action: str, payload: dict) -> bool:
        logger.info(f"[{self.provider_name}] Pushing {action} for {resource_type} to workspace {workspace_id}")
        # Simulate successful API call
        return True
        
    async def handle_webhook(self, workspace_id: str, payload: dict):
        logger.info(f"[{self.provider_name}] Received webhook for workspace {workspace_id}: {payload}")

class SlackConnector(MockConnector):
    def __init__(self):
        super().__init__("slack")

class HubSpotConnector(MockConnector):
    def __init__(self):
        super().__init__("hubspot")

class SalesforceConnector(MockConnector):
    def __init__(self):
        super().__init__("salesforce")

class ZendeskConnector(MockConnector):
    def __init__(self):
        super().__init__("zendesk")

# Register available connectors
connectors = {
    "slack": SlackConnector(),
    "hubspot": HubSpotConnector(),
    "salesforce": SalesforceConnector(),
    "zendesk": ZendeskConnector()
}

def get_connector(provider: str) -> BaseConnector:
    if provider not in connectors:
        raise ValueError(f"Unknown integration provider: {provider}")
    return connectors[provider]
