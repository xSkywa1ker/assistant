from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import enforce_idempotency, get_db_session
from ..db.models import EventLink, Provider, Task
from ..integrations.google_calendar import GoogleCalendarClient
from ..integrations.notion import NotionClient
from ..integrations.telegram import router as telegram_router
from ..schemas.integration import (
    CalendarEventRequest,
    CalendarEventResponse,
    NotionPageRequest,
    NotionPageResponse,
    TelegramNotifyRequest,
    TelegramNotifyResponse,
)

router = APIRouter()
router.include_router(telegram_router)


@router.post(
    "/calendar/events",
    response_model=CalendarEventResponse,
    dependencies=[Depends(enforce_idempotency)],
    summary="Create Google Calendar event",
)
async def create_calendar_event(
    payload: CalendarEventRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CalendarEventResponse:
    task = await session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    client = GoogleCalendarClient()
    external_id = await client.create_event(task.id, task.title, task.description, payload.start or task.due, payload.end)
    session.add(EventLink(user_id=task.user_id, task_id=task.id, provider=Provider.GOOGLE_CALENDAR, external_id=external_id))
    await session.commit()
    return CalendarEventResponse(external_id=external_id)


@router.post(
    "/notion/page",
    response_model=NotionPageResponse,
    dependencies=[Depends(enforce_idempotency)],
    summary="Create or update Notion page",
)
async def upsert_notion_page(
    payload: NotionPageRequest,
    session: AsyncSession = Depends(get_db_session),
) -> NotionPageResponse:
    task = await session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    client = NotionClient()
    external_id = await client.upsert_page(task.id, task.title, task.description)
    session.add(EventLink(user_id=task.user_id, task_id=task.id, provider=Provider.NOTION, external_id=external_id))
    await session.commit()
    return NotionPageResponse(external_id=external_id)


@router.post(
    "/telegram/notify",
    response_model=TelegramNotifyResponse,
    dependencies=[Depends(enforce_idempotency)],
    summary="Send Telegram notification",
)
async def send_telegram_notification(
    payload: TelegramNotifyRequest,
) -> TelegramNotifyResponse:
    return TelegramNotifyResponse(status="queued")
