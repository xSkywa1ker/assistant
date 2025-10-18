from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", summary="Liveness check")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", summary="Readiness check")
async def readyz() -> dict[str, str]:
    return {"status": "ready"}
