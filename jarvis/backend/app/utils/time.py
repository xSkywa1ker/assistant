from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytz


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def as_timezone(dt: datetime, tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    return dt.astimezone(tz)


def next_available_slot(start: datetime, duration: timedelta, work_hours: tuple[int, int]) -> tuple[datetime, datetime]:
    begin_hour, end_hour = work_hours
    candidate = start
    if candidate.hour < begin_hour:
        candidate = candidate.replace(hour=begin_hour, minute=0, second=0, microsecond=0)
    if candidate.hour >= end_hour:
        candidate = (candidate + timedelta(days=1)).replace(hour=begin_hour, minute=0, second=0, microsecond=0)
    end = candidate + duration
    if end.hour > end_hour or (end.hour == end_hour and end.minute > 0):
        candidate = (candidate + timedelta(days=1)).replace(hour=begin_hour, minute=0, second=0, microsecond=0)
        end = candidate + duration
    return candidate, end
