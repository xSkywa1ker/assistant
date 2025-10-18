from __future__ import annotations

import pytest
from pydantic import BaseModel

from jarvis.backend.app.llm.parsers.json_parser import parse_json_response


class SampleModel(BaseModel):
    name: str


@pytest.mark.asyncio
async def test_parse_json_response_happy_path():
    result = await parse_json_response('{"name": "Jarvis"}', SampleModel)
    assert result.name == "Jarvis"


@pytest.mark.asyncio
async def test_parse_json_response_repairs():
    raw = 'Response: {"name": "Jarvis"} extra'
    result = await parse_json_response(raw, SampleModel)
    assert result.name == "Jarvis"
