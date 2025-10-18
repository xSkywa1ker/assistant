from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_db_session
from ..memory import get_memory_store
from ..schemas.memory import MemorySearchResponse, MemorySearchResult

router = APIRouter()


@router.get("/search", response_model=MemorySearchResponse, summary="Semantic memory search")
async def search_memory(
    user_id: int,
    q: str = Query(min_length=3),
    session: AsyncSession = Depends(get_db_session),
) -> MemorySearchResponse:
    store = await get_memory_store(session)
    results = await store.search_memory(user_id, q)
    return MemorySearchResponse(
        results=[MemorySearchResult(id=memory.id, content=memory.content, kind=memory.kind, score=score) for memory, score in results]
    )
