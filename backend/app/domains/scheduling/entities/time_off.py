"""TimeOff entity for scheduling domain."""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

from ..value_objects import DayOfWeek


@dataclass
class TimeOff:
    """
    Aggregate root representing blocked time (time off) for an instructor.

    Used to block periods when the instructor is unavailable.
    """
    instructor_id: int
    start_at: datetime
    end_at: datetime
    reason: Optional[str] = None

    # For recurring weekly blocks
    is_recurring: bool = False
    recurrence_day: Optional[DayOfWeek] = None

    # Identity
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate time off after initialization."""
        self._validate()

    def _validate(self):
        """Validate time off configuration."""
        if self.start_at >= self.end_at:
            raise ValueError("Start time must be before end time")

        if self.is_recurring and self.recurrence_day is None:
            raise ValueError("Recurring time off requires recurrence_day")

    @property
    def duration_minutes(self) -> int:
        """Get duration in minutes."""
        return int((self.end_at - self.start_at).total_seconds() / 60)

    @property
    def duration_hours(self) -> float:
        """Get duration in hours."""
        return self.duration_minutes / 60

    def overlaps_with(self, start: datetime, end: datetime) -> bool:
        """Check if this time off overlaps with a given time range."""
        return self.start_at < end and self.end_at > start

    def is_active_on(self, check_date: date) -> bool:
        """Check if this time off is active on a specific date."""
        if self.is_recurring:
            return check_date.weekday() == self.recurrence_day.value
        else:
            return self.start_at.date() <= check_date <= self.end_at.date()

    def update(self, start_at: datetime, end_at: datetime, reason: Optional[str] = None):
        """Update the time off period."""
        if start_at >= end_at:
            raise ValueError("Start time must be before end time")
        self.start_at = start_at
        self.end_at = end_at
        if reason is not None:
            self.reason = reason

    @classmethod
    def create_single(
        cls,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        reason: Optional[str] = None,
    ) -> "TimeOff":
        """Factory method for creating a single time off period."""
        return cls(
            instructor_id=instructor_id,
            start_at=start_at,
            end_at=end_at,
            reason=reason,
            is_recurring=False,
        )

    @classmethod
    def create_recurring(
        cls,
        instructor_id: int,
        day_of_week: DayOfWeek,
        start_time: datetime,
        end_time: datetime,
        reason: Optional[str] = None,
    ) -> "TimeOff":
        """Factory method for creating a recurring weekly time off."""
        return cls(
            instructor_id=instructor_id,
            start_at=start_time,
            end_at=end_time,
            reason=reason,
            is_recurring=True,
            recurrence_day=day_of_week,
        )

    def __repr__(self) -> str:
        if self.is_recurring:
            return f"TimeOff(recurring, {self.recurrence_day.name})"
        return f"TimeOff({self.start_at} - {self.end_at})"
