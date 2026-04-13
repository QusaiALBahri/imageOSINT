"""Celery task queue configuration"""

from celery import Celery
from celery.signals import task_postrun, task_prerun
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "osint_image_tool",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=28 * 60,  # 28 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Task result settings
celery_app.conf.result_expires = 3600  # 1 hour


@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **kw):
    """Handle task pre-run"""
    logger.info(f"Task {task.name} started: {task_id}")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **kw):
    """Handle task post-run"""
    logger.info(f"Task {task.name} finished: {task_id}")
