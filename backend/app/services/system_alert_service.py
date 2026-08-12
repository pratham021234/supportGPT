import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import SystemEvent
from app.services.email_service import email_service
from app.services.email_template_service import email_template_service

logger = logging.getLogger(__name__)

class SystemAlertService:
    async def monitor_failures(self, db: AsyncSession, event: SystemEvent):
        """Monitors system events and alerts administrators of failures."""
        if event.event_type in ["AI_FAILURE", "VECTOR_FAILURE", "EMAIL_FAILURE", "QUEUE_FAILURE"]:
            logger.critical(f"SYSTEM ALERT: {event.event_type} - {event.payload}")
            
            # Send alert email to admins
            # In a real scenario, fetch admin emails from DB
            admin_email = "admin@supportgpt.ai"
            subject = f"CRITICAL: {event.event_type}"
            
            # Assume payload has error details
            reason = str(event.payload.get("error", "Unknown Error")) if event.payload else "Unknown Error"
            html = email_template_service.get_escalation_alert_email("System", reason)
            
            await email_service.send_email(admin_email, subject, html)

system_alert_service = SystemAlertService()
