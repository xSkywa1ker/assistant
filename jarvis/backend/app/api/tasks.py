from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import enforce_idempotency, get_db_session
from ..db.models import AuditLog, Task
from ..schemas.task import TaskCreate, TaskList, TaskRead, TaskUpdate

router = APIRouter()


@router.get("", response_model=TaskList, summary="List tasks for a user")
async def list_tasks(user_id: int, session: AsyncSession = Depends(get_db_session)) -> TaskList:
    tasks = (await session.execute(select(Task).where(Task.user_id == user_id))).scalars().all()
    return TaskList(tasks=[TaskRead.model_validate(t) for t in tasks])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_idempotency)],
    summary="Create a new task",
)
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_db_session)) -> TaskRead:
    task = Task(**payload.model_dump())
    session.add(task)
    session.add(AuditLog(user_id=payload.user_id, action="task:create", payload_json=payload.model_dump()))
    await session.commit()
    await session.refresh(task)
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    dependencies=[Depends(enforce_idempotency)],
    summary="Update a task",
)
async def update_task(task_id: int, payload: TaskUpdate, session: AsyncSession = Depends(get_db_session)) -> TaskRead:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(task, key, value)
    session.add(AuditLog(user_id=task.user_id, action="task:update", payload_json={"task_id": task_id, **payload.model_dump(exclude_none=True)}))
    await session.commit()
    await session.refresh(task)
    return TaskRead.model_validate(task)
