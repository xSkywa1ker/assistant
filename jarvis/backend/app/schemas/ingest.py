from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    text: str
    user_id: int | None = None
    source: str | None = None


class IngestTask(BaseModel):
    title: str
    subtasks: list["IngestTask"] = Field(default_factory=list)
    due: datetime | None = None
    priority: int | None = None
    tags: list[str] | None = None


class IngestGoal(BaseModel):
    title: str | None = None
    description: str | None = None


class IngestResponse(BaseModel):
    tasks: list[IngestTask] = Field(default_factory=list)
    notes: list[str] | None = None
    goal: IngestGoal | None = None
