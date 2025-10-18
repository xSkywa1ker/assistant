from __future__ import annotations

from dataclasses import dataclass

from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmailClient:
    sender: str | None = None

    async def send(self, to: str, subject: str, body: str) -> None:
        logger.info("email.send_stub", to=to, subject=subject)
