from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .base import ORMModel
from .task import TaskRead


class GoalCreate(BaseModel):
    user_id: int
    title: str
    description: str | None = None
    priority: int | None = None
    status: str = "active"
    due: datetime | None = None
    decompose: bool = False


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = None
    status: str | None = None
    due: datetime | None = None


class GoalRead(ORMModel):
    id: int
    user_id: int
    title: str
    description: str | None
    priority: int | None
    status: str
    due: datetime | None
    tasks: list[TaskRead] | None = None


class GoalList(BaseModel):
    goals: list[GoalRead]
