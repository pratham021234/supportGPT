import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.notification import NotificationDelivery, DeliveryStatus

logger = logging.getLogger(__name__)

class NotificationHealthService:
    async def get_health_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Calculates health of the notification and email delivery queue."""
        
        # Total pending (queue size)
        stmt_pending = select(func.count(NotificationDelivery.id)).where(NotificationDelivery.status == DeliveryStatus.PENDING)
        result_pending = await db.execute(stmt_pending)
        pending_count = result_pending.scalar_one_or_none() or 0
        
        # Total failed
        stmt_failed = select(func.count(NotificationDelivery.id)).where(NotificationDelivery.status == DeliveryStatus.FAILED)
        result_failed = await db.execute(stmt_failed)
        failed_count = result_failed.scalar_one_or_none() or 0
        
        # Total delivered today (simple simulation)
        stmt_delivered = select(func.count(NotificationDelivery.id)).where(NotificationDelivery.status == DeliveryStatus.DELIVERED)
        result_delivered = await db.execute(stmt_delivered)
        delivered_count = result_delivered.scalar_one_or_none() or 0
        
        status = "HEALTHY"
        if failed_count > 50:
            status = "DEGRADED"
        if pending_count > 1000:
            status = "WARNING"
            
        return {
            "status": status,
            "queue_depth": pending_count,
            "failed_deliveries": failed_count,
            "successful_deliveries": delivered_count,
            "avg_latency_ms": 320 # Simulated Celery worker latency
        }

notification_health_service = NotificationHealthService()
