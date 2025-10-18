from __future__ import annotations

from pydantic import BaseModel

from .base import MemoryKind, ORMModel


class MemorySearchResult(ORMModel):
    id: int
    content: str
    kind: MemoryKind
    score: float


class MemorySearchResponse(BaseModel):
    results: list[MemorySearchResult]
