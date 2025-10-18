from __future__ import annotations

from dataclasses import dataclass

from ..core.logging import get_logger
from ..core.settings import settings

logger = get_logger(__name__)


@dataclass
class NotionClient:
    database_id: str | None = settings.notion_database_id

    async def upsert_page(self, task_id: int, title: str, description: str | None) -> str:
        logger.info("notion.upsert_page", task_id=task_id, title=title)
        return f"notion_{task_id}"
