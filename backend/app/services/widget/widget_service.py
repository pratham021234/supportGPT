import logging
import secrets
import string
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.repositories.widget_repo import (
    widget_config_repo, widget_session_repo,
    WidgetConfigurationInternalCreate, WidgetSessionInternalCreate,
    WidgetConfiguration, WidgetSession
)
from app.repositories.conversation_repo import conversation_repo, customer_repo, ConversationInternalCreate, CustomerInternalCreate

logger = logging.getLogger(__name__)

def generate_session_token(length=32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

class WidgetConfigurationService:
    async def get_configuration(self, db: AsyncSession, agent_id: str) -> Optional[WidgetConfiguration]:
        """Public endpoint retrieval. Should probably validate that agent_id is valid."""
        return await widget_config_repo.get_by_agent(db, agent_id)

    async def get_or_create_workspace_config(self, db: AsyncSession, workspace_id: str) -> WidgetConfiguration:
        config = await widget_config_repo.get_by_workspace(db, workspace_id)
        if not config:
            config_in = WidgetConfigurationInternalCreate(workspace_id=workspace_id)
            config = await widget_config_repo.create(db, obj_in=config_in)
        return config

    async def update_configuration(self, db: AsyncSession, workspace_id: str, updates: Dict[str, Any]) -> WidgetConfiguration:
        config = await self.get_or_create_workspace_config(db, workspace_id)
        return await widget_config_repo.update(db, db_obj=config, obj_in=updates)


class WidgetSessionService:
    async def initialize_session(self, db: AsyncSession, workspace_id: str, agent_id: str, customer_id: Optional[str] = None) -> WidgetSession:
        """Called when a public user opens the widget."""
        session_token = generate_session_token()
        
        session_in = WidgetSessionInternalCreate(
            workspace_id=workspace_id,
            agent_id=agent_id,
            customer_id=customer_id,
            session_token=session_token
        )
        session = await widget_session_repo.create(db, obj_in=session_in)
        
        # Log analytics
        from app.services.analytics.analytics_service import analytics_event_service
        import asyncio
        asyncio.create_task(analytics_event_service.log_event(
            db, workspace_id, "WIDGET_OPENED", "WIDGET_SESSION", str(session.id)
        ))
        
        return session
        
    async def get_session(self, db: AsyncSession, session_token: str) -> Optional[WidgetSession]:
        return await widget_session_repo.get_by_token(db, session_token)
        
    async def start_conversation(self, db: AsyncSession, session_token: str) -> str:
        """Returns conversation ID"""
        session = await self.get_session(db, session_token)
        if not session:
            raise ValueError("Invalid session")
            
        customer_id = session.customer_id
        if not customer_id:
            cust_in = CustomerInternalCreate(
                workspace_id=str(session.workspace_id),
                name="Anonymous Visitor"
            )
            customer = await customer_repo.create(db, obj_in=cust_in)
            customer_id = customer.id
            await widget_session_repo.update(db, db_obj=session, obj_in={"customer_id": customer_id})

        conv_in = ConversationInternalCreate(
            workspace_id=str(session.workspace_id),
            agent_id=str(session.agent_id) if session.agent_id else None,
            customer_id=str(customer_id),
            is_human_active=False
        )
        
        conv = await conversation_repo.create(db, obj_in=conv_in)
        return str(conv.id)


widget_config_service = WidgetConfigurationService()
widget_session_service = WidgetSessionService()
