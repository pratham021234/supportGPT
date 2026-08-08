import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List, Callable

from app.repositories.notification_repo import (
    system_event_repo, notification_repo, preference_repo, delivery_repo,
    SystemEventInternalCreate, NotificationInternalCreate, NotificationPreferenceInternalCreate, NotificationDeliveryInternalCreate,
    SystemEvent, Notification, NotificationPreference, NotificationDelivery,
    NotificationType, NotificationStatus, NotificationPriority, DeliveryChannel, DeliveryStatus
)
from app.repositories.ticket_repo import ticket_repo

logger = logging.getLogger(__name__)

class EventBusService:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_task = None

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        
    async def publish(self, db: AsyncSession, workspace_id: str, event_type: str, entity_type: Optional[str] = None, entity_id: Optional[str] = None, actor_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None):
        """Persists the event and drops it in the async queue."""
        
        event_in = SystemEventInternalCreate(
            workspace_id=workspace_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            payload=payload
        )
        event = await system_event_repo.create(db, obj_in=event_in)
        
        # Fire and forget into the queue
        await self._queue.put((db, event))
        
    async def _worker(self):
        while True:
            db, event = await self._queue.get()
            try:
                handlers = self._subscribers.get(event.event_type, [])
                for handler in handlers:
                    await handler(db, event)
            except Exception as e:
                logger.error(f"Error processing event {event.id}: {e}")
            finally:
                self._queue.task_done()
                
    def start(self):
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._worker())

class PreferenceService:
    async def get_preferences(self, db: AsyncSession, user_id: str) -> NotificationPreference:
        pref = await preference_repo.get_by_user(db, user_id)
        if not pref:
            pref = await preference_repo.create(db, obj_in=NotificationPreferenceInternalCreate(user_id=user_id))
        return pref
        
    async def update_preferences(self, db: AsyncSession, user_id: str, updates: Dict[str, Any]) -> NotificationPreference:
        pref = await self.get_preferences(db, user_id)
        return await preference_repo.update(db, db_obj=pref, obj_in=updates)

class DeliveryTrackingService:
    async def dispatch_in_app(self, db: AsyncSession, notification: Notification):
        # We create a delivery record
        delivery_in = NotificationDeliveryInternalCreate(
            notification_id=str(notification.id),
            channel=DeliveryChannel.IN_APP,
            status=DeliveryStatus.DELIVERED
        )
        await delivery_repo.create(db, obj_in=delivery_in)
        # Note: actual push to websocket happens in the router layer or via redis pubsub
        
    async def dispatch_email(self, db: AsyncSession, notification: Notification, user_email: str):
        # Mocking email dispatch
        logger.info(f"MOCK EMAIL DISPATCH to {user_email}: {notification.title}")
        
        delivery_in = NotificationDeliveryInternalCreate(
            notification_id=str(notification.id),
            channel=DeliveryChannel.EMAIL,
            status=DeliveryStatus.DELIVERED
        )
        await delivery_repo.create(db, obj_in=delivery_in)

class NotificationService:
    async def process_event(self, db: AsyncSession, event: SystemEvent):
        """Rule Engine: converts SystemEvents into Notifications for users."""
        
        if event.event_type == "TICKET_ASSIGNED":
            # payload should contain assigned_to
            if event.payload and "assigned_to" in event.payload:
                user_id = event.payload["assigned_to"]
                
                # Check preferences
                prefs = await preference_service.get_preferences(db, user_id)
                
                # Create notification
                notif_in = NotificationInternalCreate(
                    workspace_id=str(event.workspace_id),
                    user_id=user_id,
                    title="Ticket Assigned",
                    message=f"You have been assigned to a ticket.",
                    type=NotificationType.INFO,
                    priority=NotificationPriority.MEDIUM
                )
                notif = await notification_repo.create(db, obj_in=notif_in)
                
                # Dispatch
                if prefs.in_app_enabled:
                    await delivery_service.dispatch_in_app(db, notif)
                if prefs.email_enabled:
                    await delivery_service.dispatch_email(db, notif, "mock@example.com")
                    
    async def get_unread(self, db: AsyncSession, user_id: str):
        return await notification_repo.get_unread_by_user(db, user_id)
        
    async def mark_as_read(self, db: AsyncSession, notification_id: str):
        notif = await notification_repo.get(db, id=notification_id)
        if notif:
            return await notification_repo.update(db, db_obj=notif, obj_in={"status": NotificationStatus.READ})
        return None

event_bus = EventBusService()
preference_service = PreferenceService()
delivery_service = DeliveryTrackingService()
notification_service = NotificationService()

# Register rules
event_bus.subscribe("TICKET_ASSIGNED", notification_service.process_event)
