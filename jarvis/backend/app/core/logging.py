from __future__ import annotations

import logging
from typing import Any, Dict

import structlog

from .settings import settings


def configure_logging() -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    logging.basicConfig(format="%(message)s", level=getattr(logging, settings.log_level.upper(), logging.INFO))

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            timestamper,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
