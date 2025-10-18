from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.settings import settings
from .store import MemoryStore


async def get_memory_store(session: AsyncSession) -> MemoryStore:
    # For MVP we use the database-backed store for both pgvector and qdrant settings.
    # Swapping to a remote Qdrant cluster can be implemented by extending MemoryStore.
    return MemoryStore(session=session)
