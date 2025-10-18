from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    user_id: int


class PlannedAction(BaseModel):
    task_id: int
    title: str
    suggested_slot: tuple[datetime, datetime]
    estimate_minutes: int | None = None


class PlanResponse(BaseModel):
    actions: list[PlannedAction] = Field(default_factory=list)
