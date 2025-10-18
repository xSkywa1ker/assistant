from __future__ import annotations

import asyncio

from sqlalchemy import select

from ..core.db import async_session_factory
from ..db.models import Goal, Task, TaskStatus, User


async def seed() -> None:
    async with async_session_factory() as session:
        user = (await session.execute(select(User).where(User.username == "demo"))).scalar_one_or_none()
        if not user:
            user = User(username="demo", timezone="UTC", work_hours="09:00-17:00")
            session.add(user)
            await session.flush()
        goal = Goal(user_id=user.id, title="Launch MVP", description="Ship Jarvis MVP")
        session.add(goal)
        await session.flush()
        session.add_all(
            [
                Task(user_id=user.id, goal_id=goal.id, title="Prepare roadmap", status=TaskStatus.TODO, priority=3),
                Task(user_id=user.id, goal_id=goal.id, title="Setup infra", status=TaskStatus.DOING, priority=4),
            ]
        )
        await session.commit()
        print("Seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
