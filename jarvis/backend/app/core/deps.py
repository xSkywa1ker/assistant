from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils.idempotency import IdempotencyEnforcer
from .db import get_db
from .settings import settings


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        return session
    raise RuntimeError("Failed to acquire database session")


def get_settings_dependency():
    return settings


async def enforce_idempotency(
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> IdempotencyEnforcer:
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail="Missing Idempotency-Key header")
    enforcer = IdempotencyEnforcer(settings.redis_url)
    if not await enforcer.register_key(idempotency_key):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency key already used")
    return enforcer
