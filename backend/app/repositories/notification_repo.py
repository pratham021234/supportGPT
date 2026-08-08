from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.repositories.base import BaseRepository
from app.models.notification import (
    SystemEvent, Notification, NotificationPreference, NotificationDelivery,
    NotificationType, NotificationStatus, NotificationPriority, DeliveryChannel, DeliveryStatus
)
from pydantic import BaseModel

class SystemEventInternalCreate(BaseModel):
    workspace_id: str
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    actor_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class NotificationInternalCreate(BaseModel):
    workspace_id: str
    user_id: str
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    status: NotificationStatus = NotificationStatus.UNREAD
    priority: NotificationPriority = NotificationPriority.MEDIUM

class NotificationPreferenceInternalCreate(BaseModel):
    user_id: str
    email_enabled: bool = True
    in_app_enabled: bool = True
    digest_enabled: bool = False

class NotificationDeliveryInternalCreate(BaseModel):
    notification_id: str
    channel: DeliveryChannel
    status: DeliveryStatus = DeliveryStatus.PENDING

class SystemEventRepository(BaseRepository[SystemEvent, SystemEventInternalCreate, BaseModel]):
    pass

class NotificationRepository(BaseRepository[Notification, NotificationInternalCreate, BaseModel]):
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[Notification]:
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())
        
    async def get_unread_by_user(self, db: AsyncSession, user_id: str) -> List[Notification]:
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status == NotificationStatus.UNREAD
        ).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())

class NotificationPreferenceRepository(BaseRepository[NotificationPreference, NotificationPreferenceInternalCreate, BaseModel]):
    async def get_by_user(self, db: AsyncSession, user_id: str) -> Optional[NotificationPreference]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class NotificationDeliveryRepository(BaseRepository[NotificationDelivery, NotificationDeliveryInternalCreate, BaseModel]):
    pass


system_event_repo = SystemEventRepository(SystemEvent)
notification_repo = NotificationRepository(Notification)
preference_repo = NotificationPreferenceRepository(NotificationPreference)
delivery_repo = NotificationDeliveryRepository(NotificationDelivery)
