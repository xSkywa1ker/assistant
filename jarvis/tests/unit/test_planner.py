from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from jarvis.backend.app.planner.engine import Planner


@pytest.mark.asyncio
async def test_score_prioritizes_deadlines(monkeypatch):
    planner = Planner(session=None)  # type: ignore[arg-type]

    soon = datetime.now(timezone.utc) + timedelta(hours=1)
    later = datetime.now(timezone.utc) + timedelta(days=5)

    task_urgent = SimpleNamespace(priority=3, due=soon, estimate_minutes=10)
    task_late = SimpleNamespace(priority=3, due=later, estimate_minutes=10)

    assert planner._score_task(task_urgent) > planner._score_task(task_late)


@pytest.mark.asyncio
async def test_suggest_slot_respects_work_hours():
    planner = Planner(session=None)  # type: ignore[arg-type]
    task = SimpleNamespace(estimate_minutes=30)
    start, end = planner._suggest_slot(task, (9, 17))
    assert start.hour >= 9
    assert (end - start).total_seconds() == 30 * 60
