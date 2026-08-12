import logging
import asyncio
from datetime import datetime, timedelta
from typing import Callable, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import async_session_maker

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.tasks: List[Tuple[Callable, int]] = [] # list of (task_function, interval_seconds)
        self._loop_task = None
        
    def add_job(self, func: Callable, interval_seconds: int):
        self.tasks.append((func, interval_seconds))
        
    async def _run_loop(self):
        while True:
            for func, interval in self.tasks:
                # In a real environment, we'd use celery beat or apscheduler.
                # For this mock, we just run it and assume it handles its own logic.
                try:
                    async with async_session_maker() as db:
                        await func(db)
                except Exception as e:
                    logger.error(f"Scheduler job failed: {e}")
                    
            await asyncio.sleep(60) # Wake up every minute to check schedule

    def start(self):
        if not self._loop_task:
            self._loop_task = asyncio.create_task(self._run_loop())

scheduler_service = SchedulerService()
