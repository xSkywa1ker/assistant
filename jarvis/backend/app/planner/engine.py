from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger
from ..db.models import Task, TaskStatus, User
from ..utils.time import next_available_slot, now_utc

logger = get_logger(__name__)


@dataclass
class Planner:
    session: AsyncSession

    async def pick_next_actions(self, user_id: int, limit: int = 5) -> list[tuple[Task, tuple[datetime, datetime]]]:
        user = await self.session.get(User, user_id)
        if not user:
            return []
        work_hours = self._parse_work_hours(user.work_hours)
        tasks = (
            await self.session.execute(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.status.in_([TaskStatus.TODO, TaskStatus.DOING]),
                )
            )
        ).scalars().all()
        scored = []
        for task in tasks:
            if task.waits:
                continue
            score = self._score_task(task)
            suggested = self._suggest_slot(task, work_hours)
            scored.append((task, score, suggested))
        scored.sort(key=lambda entry: entry[1], reverse=True)
        return [(task, suggested) for task, _, suggested in scored[:limit]]

    def _parse_work_hours(self, work_hours: str) -> tuple[int, int]:
        try:
            start, end = work_hours.split("-")
            start_h = int(start.split(":")[0])
            end_h = int(end.split(":")[0])
            return start_h, end_h
        except Exception:  # pragma: no cover - fallback path
            return 9, 17

    def _score_task(self, task: Task) -> float:
        score = 0.0
        if task.priority:
            score += task.priority * 10
        if task.due:
            delta = (task.due - now_utc()).total_seconds() / 3600
            score += max(0.0, 48 - delta)
        if task.estimate_minutes and task.estimate_minutes <= 25:
            score += 5
        return score

    def _suggest_slot(self, task: Task, work_hours: tuple[int, int]) -> tuple[datetime, datetime]:
        start = now_utc()
        duration = timedelta(minutes=task.estimate_minutes or 30)
        return next_available_slot(start, duration, work_hours)
