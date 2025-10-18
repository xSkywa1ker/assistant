from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..core.logging import get_logger
from ..core.settings import settings

logger = get_logger(__name__)


@dataclass
class GoogleCalendarClient:
    calendar_id: str | None = settings.google_calendar_id

    async def create_event(self, task_id: int, title: str, description: str | None, start: datetime | None, end: datetime | None) -> str:
        logger.info("google_calendar.create_event", task_id=task_id, title=title)
        if not start:
            start = datetime.utcnow()
        if not end:
            end = start + timedelta(minutes=30)
        return f"evt_{task_id}_{int(start.timestamp())}"
