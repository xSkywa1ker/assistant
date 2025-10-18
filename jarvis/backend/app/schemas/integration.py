from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CalendarEventRequest(BaseModel):
    task_id: int
    start: datetime | None = None
    end: datetime | None = None


class CalendarEventResponse(BaseModel):
    provider: str = "google_calendar"
    external_id: str


class NotionPageRequest(BaseModel):
    task_id: int
    overwrite: bool = False


class NotionPageResponse(BaseModel):
    external_id: str


class TelegramNotifyRequest(BaseModel):
    user_id: int | None = None
    chat_id: str | None = None
    message: str


class TelegramNotifyResponse(BaseModel):
    status: str = Field(default="queued")
