from __future__ import annotations

import asyncio
import hashlib
from datetime import timedelta

import aioredis

DEFAULT_TTL_SECONDS = 60 * 5


class IdempotencyEnforcer:
    def __init__(self, redis_url: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self._client: aioredis.Redis | None = None

    async def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def register_key(self, key: str) -> bool:
        client = await self._get_client()
        normalized = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return await client.set(normalized, "1", nx=True, ex=self.ttl_seconds)

    async def release(self, key: str) -> None:
        client = await self._get_client()
        normalized = hashlib.sha256(key.encode("utf-8")).hexdigest()
        await client.delete(normalized)

    async def __aenter__(self) -> "IdempotencyEnforcer":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.close()
