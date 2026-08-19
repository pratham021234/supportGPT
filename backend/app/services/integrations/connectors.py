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

import httpx
import hmac
import hashlib
import json

class WebhookDispatcher:
    async def dispatch(self, url: str, secret: str, payload: dict):
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "X-SupportGPT-Signature": f"sha256={signature}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, content=payload_bytes, headers=headers, timeout=5.0)
            except Exception as e:
                logger.error(f"Webhook dispatch failed to {url}: {e}")

class WebhookConnector(MockConnector):
    def __init__(self):
        super().__init__("webhook")
        self.dispatcher = WebhookDispatcher()
        
    async def push_data(self, workspace_id: str, resource_type: str, action: str, payload: dict, url: str = None, secret: str = "default_secret") -> bool:
        if url:
            await self.dispatcher.dispatch(url, secret, {"action": action, "resource_type": resource_type, "data": payload})
        return True

class SlackConnector(MockConnector):
    def __init__(self):
        super().__init__("slack")

    async def push_data(self, workspace_id: str, resource_type: str, action: str, payload: dict, webhook_url: str = None) -> bool:
        if not webhook_url: return True
        
        text = f"*SupportGPT Alert:* {action} on {resource_type}"
        slack_payload = {
            "text": text,
            "attachments": [
                {
                    "color": "#36a64f",
                    "fields": [{"title": k, "value": str(v), "short": True} for k, v in list(payload.items())[:5]]
                }
            ]
        }
        async with httpx.AsyncClient() as client:
            try: await client.post(webhook_url, json=slack_payload, timeout=5.0)
            except Exception as e: logger.error(f"Slack failed: {e}")
        return True

class MicrosoftTeamsConnector(MockConnector):
    def __init__(self):
        super().__init__("teams")

    async def push_data(self, workspace_id: str, resource_type: str, action: str, payload: dict, webhook_url: str = None) -> bool:
        if not webhook_url: return True
        
        teams_payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": f"SupportGPT: {action}",
            "sections": [{
                "activityTitle": f"SupportGPT Alert: {action} on {resource_type}",
                "facts": [{"name": k, "value": str(v)} for k, v in list(payload.items())[:5]],
                "markdown": True
            }]
        }
        async with httpx.AsyncClient() as client:
            try: await client.post(webhook_url, json=teams_payload, timeout=5.0)
            except Exception as e: logger.error(f"Teams failed: {e}")
        return True

class DiscordConnector(MockConnector):
    def __init__(self):
        super().__init__("discord")

    async def push_data(self, workspace_id: str, resource_type: str, action: str, payload: dict, webhook_url: str = None) -> bool:
        if not webhook_url: return True
        
        discord_payload = {
            "content": f"**SupportGPT Alert:** {action} on {resource_type}",
            "embeds": [{
                "title": "Details",
                "color": 5814783,
                "fields": [{"name": k, "value": str(v), "inline": True} for k, v in list(payload.items())[:5]]
            }]
        }
        async with httpx.AsyncClient() as client:
            try: await client.post(webhook_url, json=discord_payload, timeout=5.0)
            except Exception as e: logger.error(f"Discord failed: {e}")
        return True

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
    "teams": MicrosoftTeamsConnector(),
    "discord": DiscordConnector(),
    "webhook": WebhookConnector(),
    "hubspot": HubSpotConnector(),
    "salesforce": SalesforceConnector(),
    "zendesk": ZendeskConnector()
}

def get_connector(provider: str) -> BaseConnector:
    if provider not in connectors:
        raise ValueError(f"Unknown integration provider: {provider}")
    return connectors[provider]
