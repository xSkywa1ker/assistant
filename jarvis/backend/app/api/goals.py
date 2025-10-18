from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import enforce_idempotency, get_db_session
from ..db.models import AuditLog, Goal, Task, TaskStatus
from ..schemas.goal import GoalCreate, GoalList, GoalRead, GoalUpdate

router = APIRouter()


@router.get("", response_model=GoalList, summary="List goals for a user")
async def list_goals(user_id: int, session: AsyncSession = Depends(get_db_session)) -> GoalList:
    goals = (await session.execute(select(Goal).where(Goal.user_id == user_id))).scalars().all()
    return GoalList(goals=[GoalRead.model_validate(goal) for goal in goals])


@router.post(
    "",
    response_model=GoalRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_idempotency)],
    summary="Create a goal",
)
async def create_goal(payload: GoalCreate, session: AsyncSession = Depends(get_db_session)) -> GoalRead:
    goal = Goal(**payload.model_dump(exclude={"decompose"}))
    session.add(goal)
    await session.flush()

    if payload.decompose:
        seed_task = Task(
            user_id=payload.user_id,
            goal_id=goal.id,
            title=f"Plan: {goal.title}",
            status=TaskStatus.TODO,
            priority=payload.priority,
            due=payload.due,
        )
        session.add(seed_task)

    session.add(AuditLog(user_id=payload.user_id, action="goal:create", payload_json=payload.model_dump()))
    await session.commit()
    await session.refresh(goal)
    return GoalRead.model_validate(goal)


@router.patch(
    "/{goal_id}",
    response_model=GoalRead,
    dependencies=[Depends(enforce_idempotency)],
    summary="Update a goal",
)
async def update_goal(goal_id: int, payload: GoalUpdate, session: AsyncSession = Depends(get_db_session)) -> GoalRead:
    goal = await session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(goal, key, value)
    session.add(AuditLog(user_id=goal.user_id, action="goal:update", payload_json={"goal_id": goal_id, **payload.model_dump(exclude_none=True)}))
    await session.commit()
    await session.refresh(goal)
    return GoalRead.model_validate(goal)
