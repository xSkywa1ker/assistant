from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger
from ..db.models import MemoryChunk, MemoryKind
from ..llm.client import a_embed

logger = get_logger(__name__)


@dataclass
class MemoryStore:
    session: AsyncSession

    async def add_memory(self, user_id: int, kind: MemoryKind, content: str) -> MemoryChunk:
        checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
        existing = await self.session.scalar(select(MemoryChunk).where(MemoryChunk.embedding_checksum == checksum))
        if existing:
            return existing
        embedding = await self._embed(content)
        memory = MemoryChunk(user_id=user_id, kind=kind, content=content, embedding=embedding, embedding_checksum=checksum)
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def search_memory(self, user_id: int, query: str, top_k: int = 8) -> list[tuple[MemoryChunk, float]]:
        embedding = await self._embed(query)
        rows = (await self.session.execute(select(MemoryChunk).where(MemoryChunk.user_id == user_id))).scalars().all()
        results: list[tuple[MemoryChunk, float]] = []
        for row in rows:
            if not row.embedding:
                continue
            sim = cosine_similarity(embedding, row.embedding)
            results.append((row, sim))
        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]

    async def _embed(self, text: str) -> list[float]:
        vectors = await a_embed([text])
        vector = vectors[0] if vectors else []
        if not vector:
            return simple_sentence_embedding(text)
        return vector


def cosine_similarity(vec_a: Iterable[float], vec_b: Iterable[float]) -> float:
    a = np.array(list(vec_a))
    b = np.array(list(vec_b))
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def simple_sentence_embedding(text: str) -> list[float]:
    tokens = text.lower().split()
    vocab = sorted(set(tokens))
    vector = [tokens.count(token) for token in vocab]
    if not vector:
        return [0.0]
    norm = np.linalg.norm(vector)
    return [float(v / norm) for v in vector]
