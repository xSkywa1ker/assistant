from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.router import api_router
from .core.logging import configure_logging
from .core.settings import settings

configure_logging()


@asynccontextmanager
def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Jarvis MVP assistant API",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Health probes"},
        {"name": "ingest", "description": "Normalize user input into tasks"},
        {"name": "planner", "description": "Next best actions"},
        {"name": "tasks", "description": "Task management"},
        {"name": "goals", "description": "Goal management"},
        {"name": "memory", "description": "Knowledge memory"},
        {"name": "integrations", "description": "External integrations"},
    ],
)

app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def index() -> dict[str, str]:
    return {"message": "Jarvis is online"}
