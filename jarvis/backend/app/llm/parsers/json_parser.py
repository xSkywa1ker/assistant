from __future__ import annotations

import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


async def parse_json_response(raw: str, model: Type[T]) -> T:
    last_error: Exception | None = None
    for _ in range(2):
        try:
            data = json.loads(raw)
            return model.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:  # pragma: no cover - loops ensures reliability
            last_error = exc
            raw = await _repair_json(raw)
    raise ValueError(f"Failed to parse LLM response: {last_error}")


async def _repair_json(raw: str) -> str:
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start : end + 1]
    return "{}"
