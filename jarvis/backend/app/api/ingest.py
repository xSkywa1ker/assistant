from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import enforce_idempotency, get_db_session
from ..core.logging import get_logger
from ..db.models import AuditLog, Goal, Note, Task, TaskStatus, MemoryKind
from ..llm.service import normalize_text
from ..memory import get_memory_store
from ..schemas.ingest import IngestRequest, IngestResponse, IngestTask

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "",
    response_model=IngestResponse,
    summary="Ingest raw text and normalize into structured tasks",
    responses={
        400: {"description": "Missing user context"},
        500: {"description": "LLM normalization failed"},
    },
)
async def ingest_text(
    payload: IngestRequest,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(enforce_idempotency),
) -> IngestResponse:
    if not payload.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")

    parsed = await normalize_text(payload.text)
    created_tasks: list[Task] = []

    async def create_task(task_payload: IngestTask, parent_id: int | None = None) -> Task:
        task = Task(
            user_id=payload.user_id,
            title=task_payload.title,
            status=TaskStatus.TODO,
            priority=task_payload.priority,
            due=task_payload.due,
            parent_id=parent_id,
            source=payload.source,
        )
        session.add(task)
        await session.flush()
        for sub in task_payload.subtasks:
            await create_task(sub, parent_id=task.id)
        return task

    goal_obj: Goal | None = None
    if parsed.goal and parsed.goal.title:
        goal_obj = Goal(
            user_id=payload.user_id,
            title=parsed.goal.title,
            description=parsed.goal.description,
        )
        session.add(goal_obj)
        await session.flush()

    for task_payload in parsed.tasks:
        task = await create_task(task_payload)
        if goal_obj:
            task.goal_id = goal_obj.id
        created_tasks.append(task)

    if parsed.notes:
        for note in parsed.notes:
            session.add(Note(user_id=payload.user_id, content=note))

    session.add(
        AuditLog(
            user_id=payload.user_id,
            action="ingest",
            payload_json={"source": payload.source, "task_count": len(parsed.tasks)},
        )
    )
    await session.commit()

    memory_store = await get_memory_store(session)
    for task in created_tasks:
        await memory_store.add_memory(payload.user_id, kind=MemoryKind.CONTEXT, content=task.title)

    return parsed
