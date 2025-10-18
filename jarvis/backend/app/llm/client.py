import asyncio
from typing import Any, Dict, List, Optional

import httpx

from backend.app.core.settings import get_settings


def _get_settings():
    return get_settings()


# OpenAI-compatible (Groq) client
_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError("Install 'openai' package to use OPENAI provider") from exc
        settings = _get_settings()
        base_url = settings.openai_base_url
        api_key = settings.openai_api_key
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        _openai_client = OpenAI(base_url=base_url, api_key=api_key)
    return _openai_client


def _reset_openai_client():
    global _openai_client
    _openai_client = None


def _ollama_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    settings = _get_settings()
    base = settings.ollama_base_url.rstrip("/")
    model_name = model or settings.ollama_model or "llama3.1"
    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    with httpx.Client(timeout=60) as client:
        response = client.post(f"{base}/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _ollama_embed(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    settings = _get_settings()
    base = settings.ollama_base_url.rstrip("/")
    model_name = model or "nomic-embed-text"
    payload = {"model": model_name, "input": texts}
    with httpx.Client(timeout=60) as client:
        response = client.post(f"{base}/v1/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]


def chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    settings = _get_settings()
    provider = settings.llm_provider.lower()
    if provider == "openai":
        client = _get_openai_client()
        use_model = model or settings.openai_model
        response = client.chat.completions.create(
            model=use_model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    if provider == "ollama":
        return _ollama_chat(messages, model=model, temperature=temperature)
    raise ValueError(f"Unsupported LLM_PROVIDER={provider}")


def embed(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    settings = _get_settings()
    provider = settings.llm_provider.lower()
    if provider == "openai":
        client = _get_openai_client()
        use_model = model or settings.openai_embedding_model
        response = client.embeddings.create(model=use_model, input=texts)
        embeddings: List[List[float]] = []
        for item in response.data:
            embedding = getattr(item, "embedding", None)
            if embedding is None:
                embedding = item["embedding"]  # type: ignore[index]
            embeddings.append(list(embedding))
        return embeddings
    if provider == "ollama":
        return _ollama_embed(texts, model=model)
    raise ValueError(f"Unsupported LLM_PROVIDER={provider}")


async def a_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    return await asyncio.to_thread(chat, messages, model, temperature)


async def a_embed(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    return await asyncio.to_thread(embed, texts, model)


__all__ = [
    "chat",
    "embed",
    "a_chat",
    "a_embed",
    "_reset_openai_client",
]
