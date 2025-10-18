from __future__ import annotations

from fastapi import APIRouter

from . import goals, health, ingest, integrations, memory, plan, tasks

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(plan.router, prefix="/plan", tags=["planner"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
