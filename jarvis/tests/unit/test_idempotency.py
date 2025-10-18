from __future__ import annotations

import pytest

from jarvis.backend.app.utils.idempotency import IdempotencyEnforcer


class DummyRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def set(self, key: str, value: str, nx: bool = False, ex: int | None = None) -> bool:
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)

    async def close(self) -> None:  # pragma: no cover - noop
        return None


@pytest.mark.asyncio
async def test_idempotency_register(monkeypatch):
    dummy = DummyRedis()

    async def fake_from_url(url: str, decode_responses: bool = True):
        return dummy

    monkeypatch.setattr("aioredis.from_url", fake_from_url)

    enforcer = IdempotencyEnforcer("redis://local")
    assert await enforcer.register_key("abc")
    assert not await enforcer.register_key("abc")
