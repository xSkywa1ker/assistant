from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ..core.deps import get_settings_dependency
from ..core.logging import get_logger
from ..core.settings import Settings

logger = get_logger(__name__)


@dataclass
class TelegramClient:
    bot_token: str | None

    async def notify(self, chat_id: str, text: str) -> str:
        logger.info("telegram.notify", chat_id=chat_id, text=text)
        return "sent"


router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/notify")
async def notify(
    payload: dict[str, str],
    settings: Settings = Depends(get_settings_dependency),
):
    client = TelegramClient(bot_token=settings.telegram_bot_token)
    chat_id = payload.get("chat_id") or payload.get("user_id", "")
    if not chat_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="chat_id or user_id required")
    status_value = await client.notify(chat_id=str(chat_id), text=payload.get("message", ""))
    return {"status": status_value}


@router.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_secret: str | None = Header(default=None, alias="X-Telegram-Secret"),
    settings: Settings = Depends(get_settings_dependency),
):
    if settings.telegram_webhook_secret and x_telegram_secret != settings.telegram_webhook_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret")
    payload = await request.json()
    logger.info("telegram.webhook", payload=payload)
    return {"ok": True}
