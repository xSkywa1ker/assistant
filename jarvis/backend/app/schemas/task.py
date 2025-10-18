from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .base import ORMModel, TaskStatus


class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    priority: int | None = Field(default=None, ge=1, le=5)
    estimate_minutes: int | None = Field(default=None, ge=1)
    due: datetime | None = None
    goal_id: int | None = None
    parent_id: int | None = None
    source: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    estimate_minutes: int | None = Field(default=None, ge=1)
    due: datetime | None = None
    goal_id: int | None = None
    parent_id: int | None = None


class TaskRead(ORMModel):
    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int | None
    estimate_minutes: int | None
    due: datetime | None
    goal_id: int | None
    parent_id: int | None
    source: str | None
    external_ref: str | None
    created_at: datetime


class TaskList(BaseModel):
    tasks: list[TaskRead]
