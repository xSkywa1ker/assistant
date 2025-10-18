from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ORMModel(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    wait = "wait"
    done = "done"
    cancel = "cancel"


class Provider(str, Enum):
    google_calendar = "google_calendar"
    notion = "notion"
    telegram = "telegram"


class MemoryKind(str, Enum):
    profile = "profile"
    long_term = "long_term"
    context = "context"
