import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.repositories.integration_repo import (
    integration_conn_repo, integration_sync_repo, 
    IntegrationSyncLogInternalCreate, SyncStatus
)
from app.services.integrations.connectors import get_connector
from app.models.notification import SystemEvent
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class SyncEngine:
    async def process_event(self, db: AsyncSession, event: SystemEvent):
        """
        Listens to SystemEvents (e.g. from the EventBus) and routes them to active connectors.
        """
        # We want to push 'TICKET_CREATED' to HubSpot and Slack, for example.
        if event.event_type not in ["TICKET_CREATED", "TICKET_UPDATED", "MESSAGE_CREATED"]:
            return
            
        # Get all active connections for this workspace
        connections = await integration_conn_repo.get_by_workspace(db, str(event.workspace_id))
        active_conns = [c for c in connections if c.status.value == "CONNECTED"]
        
        for conn in active_conns:
            connector = None
            try:
                connector = get_connector(conn.provider)
            except ValueError:
                continue
                
            # Log the attempt
            resource_type = "ticket" if "TICKET" in event.event_type else "message"
            action = "CREATE" if "CREATED" in event.event_type else "UPDATE"
            
            # Use event payload id if present, else fallback
            resource_id = str(event.payload.get("ticket_id", event.payload.get("id", "unknown")))
            
            log_in = IntegrationSyncLogInternalCreate(
                workspace_id=str(event.workspace_id),
                connection_id=str(conn.id),
                provider=conn.provider,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                status=SyncStatus.PENDING,
                payload_snapshot=event.payload
            )
            sync_log = await integration_sync_repo.create(db, obj_in=log_in)
            
            # Push async to avoid blocking
            asyncio.create_task(self._push_and_update(str(sync_log.id), connector, str(event.workspace_id), resource_type, action, event.payload))


    async def _push_and_update(self, log_id: str, connector, workspace_id: str, resource_type: str, action: str, payload: dict):
        """Background task to execute the push and update the log status."""
        async with SessionLocal() as db:
            sync_log = await integration_sync_repo.get(db, id=log_id)
            if not sync_log:
                return
                
            try:
                success = await connector.push_data(workspace_id, resource_type, action, payload)
                status = SyncStatus.SUCCESS if success else SyncStatus.FAILED
                
                await integration_sync_repo.update(db, db_obj=sync_log, obj_in={"status": status})
            except Exception as e:
                logger.error(f"Sync error for log {log_id}: {str(e)}")
                await integration_sync_repo.update(db, db_obj=sync_log, obj_in={
                    "status": SyncStatus.FAILED,
                    "error_message": str(e)
                })

sync_engine = SyncEngine()
