from __future__ import annotations

from pathlib import Path

from ..core.logging import get_logger
from ..schemas.ingest import IngestResponse
from .client import a_chat
from .parsers.json_parser import parse_json_response

logger = get_logger(__name__)

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8")


async def normalize_text(text: str) -> IngestResponse:
    system_prompt = load_prompt("normalize_task.prompt")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Input:\n{text}\n"},
    ]
    raw = await a_chat(messages, temperature=0.2)
    return await parse_json_response(raw, IngestResponse)
