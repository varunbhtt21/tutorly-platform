"""
Datetime utilities for consistent timezone handling.

This module provides utilities for safely comparing and manipulating datetimes
across the application, handling the mix of timezone-aware and naive datetimes.

ARCHITECTURE DECISION:
- Database stores naive datetimes (assumed to be UTC)
- Application code should use these utilities for datetime comparisons
- All comparisons normalize datetimes to the same timezone format
"""

from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """
    Get current UTC time as a naive datetime.

    This matches the format used in the database (naive UTC datetimes).
    Use this instead of datetime.utcnow() or datetime.now(timezone.utc).

    Returns:
        Naive datetime representing current UTC time
    """
    return datetime.utcnow()


def to_naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert a datetime to naive UTC format.

    If the datetime is timezone-aware, converts to UTC and removes tzinfo.
    If the datetime is naive, assumes it's already UTC and returns as-is.

    Args:
        dt: Datetime to convert (can be naive or aware)

    Returns:
        Naive datetime in UTC, or None if input is None
    """
    if dt is None:
        return None

    if dt.tzinfo is not None:
        # Convert to UTC first, then make naive
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.replace(tzinfo=None)

    # Already naive, assume UTC
    return dt


def to_aware_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert a datetime to timezone-aware UTC format.

    If the datetime is naive, assumes it's UTC and adds tzinfo.
    If the datetime is already timezone-aware, converts to UTC.

    Args:
        dt: Datetime to convert (can be naive or aware)

    Returns:
        Timezone-aware datetime in UTC, or None if input is None
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        # Naive datetime, assume UTC
        return dt.replace(tzinfo=timezone.utc)

    # Already aware, convert to UTC
    return dt.astimezone(timezone.utc)


def is_in_progress(start_at: datetime, end_at: datetime, now: Optional[datetime] = None) -> bool:
    """
    Check if a time range is currently in progress.

    Safely compares datetimes regardless of whether they are naive or aware,
    by normalizing all to naive UTC format.

    Args:
        start_at: Start time of the range
        end_at: End time of the range
        now: Current time (defaults to utc_now() if not provided)

    Returns:
        True if now is between start_at and end_at (inclusive start, exclusive end)
    """
    if now is None:
        now = utc_now()

    # Normalize all to naive UTC for safe comparison
    start_naive = to_naive_utc(start_at)
    end_naive = to_naive_utc(end_at)
    now_naive = to_naive_utc(now)

    return start_naive <= now_naive < end_naive


def has_started(start_at: datetime, now: Optional[datetime] = None) -> bool:
    """
    Check if a time has already started.

    Args:
        start_at: Start time to check
        now: Current time (defaults to utc_now() if not provided)

    Returns:
        True if start_at is in the past or present
    """
    if now is None:
        now = utc_now()

    start_naive = to_naive_utc(start_at)
    now_naive = to_naive_utc(now)

    return start_naive <= now_naive


def has_ended(end_at: datetime, now: Optional[datetime] = None) -> bool:
    """
    Check if a time has already ended.

    Args:
        end_at: End time to check
        now: Current time (defaults to utc_now() if not provided)

    Returns:
        True if end_at is in the past
    """
    if now is None:
        now = utc_now()

    end_naive = to_naive_utc(end_at)
    now_naive = to_naive_utc(now)

    return end_naive <= now_naive
