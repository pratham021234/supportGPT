from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConnector(ABC):
    """Unified interface for all third-party integrations."""
    
    @abstractmethod
    async def connect(self, workspace_id: str, auth_code: str) -> dict:
        """Exchanges an OAuth code for access tokens."""
        pass
        
    @abstractmethod
    async def disconnect(self, workspace_id: str):
        """Revokes tokens and cleans up remote webhooks if necessary."""
        pass
        
    @abstractmethod
    async def push_data(self, workspace_id: str, resource_type: str, action: str, payload: dict) -> bool:
        """Pushes data from SupportGPT out to the third party (e.g. syncing a ticket to HubSpot)."""
        pass
        
    @abstractmethod
    async def handle_webhook(self, workspace_id: str, payload: dict):
        """Processes incoming events from the third party (e.g. new message in Slack)."""
        pass
