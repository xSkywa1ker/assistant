from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from ..core.settings import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class LLMClient(Protocol):
    async def complete(self, prompt: str) -> str: ...

    async def embeddings(self, text: str) -> list[float]: ...


@dataclass
class OllamaClient:
    base_url: str
    model: str

    async def complete(self, prompt: str) -> str:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            response = await client.post("/api/generate", json={"model": self.model, "prompt": prompt})
            response.raise_for_status()
            return response.json().get("response", "")

    async def embeddings(self, text: str) -> list[float]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            response = await client.post("/api/embeddings", json={"model": self.model, "prompt": text})
            response.raise_for_status()
            return response.json().get("embedding", [])


@dataclass
class OpenAICompatClient:
    base_url: str
    api_key: str
    model: str = "gpt-4o-mini"

    async def complete(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=60) as client:
            payload = {
                "model": self.model,
                "messages": [{"role": "system", "content": "You are Jarvis."}, {"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            }
            response = await client.post("/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def embeddings(self, text: str) -> list[float]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=60) as client:
            response = await client.post("/v1/embeddings", json={"model": self.model, "input": text})
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "ollama":
        return OllamaClient(base_url=settings.ollama_base_url, model=settings.ollama_model)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key or not settings.openai_base_url:
            raise RuntimeError("OPENAI_* settings required when LLM_PROVIDER=openai")
        return OpenAICompatClient(base_url=str(settings.openai_base_url), api_key=settings.openai_api_key)
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
