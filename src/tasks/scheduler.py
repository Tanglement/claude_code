"""Task scheduler using APScheduler."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """Task scheduler for periodic jobs."""

    def __init__(self):
        """Initialize scheduler."""
        self.scheduler = BackgroundScheduler()
        self.jobs = {}

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler shutdown")

    def add_cron_job(self, func, job_id: str, hour: int, minute: int = 0, **kwargs):
        """Add a cron job.

        Args:
            func: Function to execute
            job_id: Unique job ID
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            **kwargs: Additional arguments for the function
        """
        trigger = CronTrigger(hour=hour, minute=minute)
        job = self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        self.jobs[job_id] = job
        logger.info(f"Cron job added: {job_id} at {hour}:{minute:02d}")
        return job

    def add_interval_job(self, func, job_id: str, seconds: int = None,
                        minutes: int = None, hours: int = None, **kwargs):
        """Add an interval job.

        Args:
            func: Function to execute
            job_id: Unique job ID
            seconds: Interval in seconds
            minutes: Interval in minutes
            hours: Interval in hours
            **kwargs: Additional arguments for the function
        """
        trigger_kwargs = {}
        if seconds:
            trigger_kwargs['seconds'] = seconds
        if minutes:
            trigger_kwargs['minutes'] = minutes
        if hours:
            trigger_kwargs['hours'] = hours

        trigger = IntervalTrigger(**trigger_kwargs)
        job = self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        self.jobs[job_id] = job
        logger.info(f"Interval job added: {job_id}")
        return job

    def remove_job(self, job_id: str):
        """Remove a job.

        Args:
            job_id: Job ID to remove
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Job removed: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")

    def get_job(self, job_id: str):
        """Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job object or None
        """
        return self.scheduler.get_job(job_id)

    def get_jobs(self):
        """Get all jobs.

        Returns:
            List of jobs
        """
        return self.scheduler.get_jobs()

    def list_jobs(self):
        """List all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            logger.info(f"Job: {job.id}, Next run: {job.next_run_time}")


# Global scheduler instance
_scheduler: TaskScheduler = None


def get_scheduler() -> TaskScheduler:
    """Get global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def init_scheduler() -> TaskScheduler:
    """Initialize and return scheduler with default jobs."""
    scheduler = get_scheduler()
    scheduler.start()

    # Register default jobs
    from .jobs import (
        collect_realtime_quotes,
        collect_news,
        collect_announcements,
        update_history_data,
        backup_data
    )

    # Realtime quotes - every 3 seconds
    scheduler.add_interval_job(
        collect_realtime_quotes,
        'collect_realtime',
        seconds=3
    )

    # News collection - every hour
    scheduler.add_interval_job(
        collect_news,
        'collect_news',
        hours=1
    )

    # Announcements - every hour
    scheduler.add_interval_job(
        collect_announcements,
        'collect_announcements',
        hours=1
    )

    # History update - 17:00 daily
    scheduler.add_cron_job(
        update_history_data,
        'update_history',
        hour=17,
        minute=0
    )

    # Backup - 23:00 daily
    scheduler.add_cron_job(
        backup_data,
        'backup_data',
        hour=23,
        minute=0
    )

    logger.info("Default jobs registered")
    return scheduler
