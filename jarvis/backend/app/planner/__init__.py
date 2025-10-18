from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import Planner


async def get_planner(session: AsyncSession) -> Planner:
    return Planner(session=session)
