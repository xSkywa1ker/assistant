from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_db_session
from ..planner import get_planner
from ..schemas.planner import PlanRequest, PlanResponse, PlannedAction

router = APIRouter()


@router.post("/next", response_model=PlanResponse, summary="Suggest next best actions")
async def plan_next(payload: PlanRequest, session: AsyncSession = Depends(get_db_session)) -> PlanResponse:
    planner = await get_planner(session)
    actions = await planner.pick_next_actions(payload.user_id, limit=5)
    return PlanResponse(
        actions=[
            PlannedAction(task_id=task.id, title=task.title, suggested_slot=slot, estimate_minutes=task.estimate_minutes)
            for task, slot in actions
        ]
    )
