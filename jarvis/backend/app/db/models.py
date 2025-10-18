from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    WAIT = "wait"
    DONE = "done"
    CANCEL = "cancel"


class MemoryKind(str, Enum):
    PROFILE = "profile"
    LONG_TERM = "long_term"
    CONTEXT = "context"


class Provider(str, Enum):
    GOOGLE_CALENDAR = "google_calendar"
    NOTION = "notion"
    TELEGRAM = "telegram"


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    work_hours: Mapped[str] = mapped_column(String(15), default="09:00-17:00")
    preferences_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Goal(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="goals")
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")


class Task(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("task.id", ondelete="SET NULL"), nullable=True)
    goal_id: Mapped[int | None] = mapped_column(ForeignKey("goal.id", ondelete="SET NULL"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.TODO, index=True)
    priority: Mapped[int | None] = mapped_column(Integer, CheckConstraint("priority BETWEEN 1 AND 5"), nullable=True)
    estimate_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    external_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="tasks", foreign_keys=[user_id])
    goal: Mapped[Goal | None] = relationship(back_populates="tasks")
    parent: Mapped["Task" | None] = relationship(remote_side="Task.id")
    waits: Mapped[list["Wait"]] = relationship(back_populates="task")
    event_links: Mapped[list["EventLink"]] = relationship(back_populates="task")


class Wait(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id", ondelete="CASCADE"))
    wait_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_actor: Mapped[str | None] = mapped_column(String(255), nullable=True)

    task: Mapped[Task] = relationship(back_populates="waits")


class EventLink(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id", ondelete="CASCADE"), index=True)
    provider: Mapped[Provider] = mapped_column(SAEnum(Provider))
    external_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped[Task] = relationship(back_populates="event_links")


class Note(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MemoryChunk(Base):
    __tablename__ = "memory_chunk"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    kind: Mapped[MemoryKind] = mapped_column(SAEnum(MemoryKind), index=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(ARRAY(Float), nullable=True)
    embedding_checksum: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)


class AuditLog(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(255))
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


__all__ = [
    "User",
    "Goal",
    "Task",
    "Wait",
    "EventLink",
    "Note",
    "MemoryChunk",
    "AuditLog",
    "TaskStatus",
    "MemoryKind",
    "Provider",
]
