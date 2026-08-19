import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.services.analytics.analytics_service import metrics_service
from app.services.email_service import email_service
from app.services.notifications.template_service import template_service
from app.repositories.workspace_repo import workspace_repo
from app.models.user import UserRole
from app.core.config import settings

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        if not self.is_running:
            # Add jobs
            self.scheduler.add_job(
                self.send_weekly_reports,
                CronTrigger(day_of_week='mon', hour=8, minute=0),
                id='weekly_reports',
                replace_existing=True
            )
            # Example SLA Check running every 15 minutes
            self.scheduler.add_job(
                self.check_sla_breaches,
                CronTrigger(minute='*/15'),
                id='sla_checks',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started.")

    def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped.")

    async def send_weekly_reports(self):
        logger.info("Running job: send_weekly_reports")
        async with SessionLocal() as db:
            workspaces = await workspace_repo.get_all(db) # Needs internal pagination in real life
            for ws in workspaces:
                metrics = await metrics_service.get_dashboard_metrics(db, str(ws.id), "7d")
                html = template_service.get_weekly_report_template(metrics, f"{settings.FRONTEND_URL}/dashboard/analytics")
                
                # Fetch admins of the workspace to send emails to
                # Assuming workspace has members relation, we'd iterate over them. 
                # For MVP, we'll log it.
                logger.info(f"Would dispatch weekly report to admins of {ws.name}")
                await email_service.send_email("admin@mock.com", f"Weekly Report: {ws.name}", html)

    async def check_sla_breaches(self):
        logger.info("Running job: check_sla_breaches")
        # Query open tickets older than SLA threshold, escalate them if needed
        # and publish an event to EventBus.
        pass

scheduler = SchedulerService()
