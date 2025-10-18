from __future__ import annotations

from celery import Celery

from ..core.settings import settings

celery_app = Celery(
    "jarvis",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
)

celery_app.conf.beat_schedule = {
    "daily-digest": {
        "task": "jarvis.backend.app.workers.tasks.daily_digest",
        "schedule": 60 * 60 * 24,
        "args": (1,),
    },
    "reindex-memory": {
        "task": "jarvis.backend.app.workers.tasks.reindex_memory",
        "schedule": 60 * 60,
    },
}
