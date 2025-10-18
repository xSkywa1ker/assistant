from __future__ import annotations

from celery import shared_task

from ..core.logging import get_logger

logger = get_logger(__name__)


@shared_task
def send_reminder(task_id: int) -> str:
    logger.info("tasks.send_reminder", task_id=task_id)
    return "ok"


@shared_task
def daily_digest(user_id: int) -> str:
    logger.info("tasks.daily_digest", user_id=user_id)
    return "sent"


@shared_task
def reindex_memory() -> str:
    logger.info("tasks.reindex_memory")
    return "queued"
