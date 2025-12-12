"""RecurrenceRule value object for scheduling domain."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List, Optional


class DayOfWeek(Enum):
    """Days of the week (ISO standard: Monday=0)."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def from_int(cls, value: int) -> "DayOfWeek":
        """Create from integer value."""
        for day in cls:
            if day.value == value:
                return day
        raise ValueError(f"Invalid day of week: {value}")

    @classmethod
    def from_string(cls, value: str) -> "DayOfWeek":
        """Create from string value."""
        return cls[value.upper()]


class RecurrenceFrequency(Enum):
    """Frequency of recurrence."""
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass(frozen=True)
class RecurrenceRule:
    """
    Immutable value object representing a recurrence pattern.

    Used for recurring availability and recurring sessions.
    """
    frequency: RecurrenceFrequency
    days_of_week: List[DayOfWeek]
    start_date: date
    end_date: Optional[date] = None  # None means indefinite

    def __post_init__(self):
        """Validate the recurrence rule."""
        if self.frequency == RecurrenceFrequency.WEEKLY and not self.days_of_week:
            raise ValueError("Weekly recurrence requires at least one day of week")

        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be after start date")

        # Ensure days_of_week is a sorted tuple for immutability
        if self.days_of_week:
            object.__setattr__(
                self,
                'days_of_week',
                tuple(sorted(self.days_of_week, key=lambda d: d.value))
            )

    def is_active_on(self, check_date: date) -> bool:
        """Check if this recurrence is active on a specific date."""
        # Check date range
        if check_date < self.start_date:
            return False
        if self.end_date and check_date > self.end_date:
            return False

        # Check day of week
        if self.frequency == RecurrenceFrequency.WEEKLY:
            day = DayOfWeek.from_int(check_date.weekday())
            return day in self.days_of_week

        return True  # Daily frequency

    def get_next_occurrence(self, from_date: date) -> Optional[date]:
        """Get the next occurrence date from a given date."""
        if self.end_date and from_date > self.end_date:
            return None

        current = max(from_date, self.start_date)

        if self.frequency == RecurrenceFrequency.DAILY:
            return current

        # Weekly frequency - find next matching day
        for i in range(7):
            check_date = current
            if i > 0:
                from datetime import timedelta
                check_date = current + timedelta(days=i)

            if self.end_date and check_date > self.end_date:
                return None

            day = DayOfWeek.from_int(check_date.weekday())
            if day in self.days_of_week:
                return check_date

        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "frequency": self.frequency.value,
            "days_of_week": [d.value for d in self.days_of_week],
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecurrenceRule":
        """Create from dictionary."""
        return cls(
            frequency=RecurrenceFrequency(data["frequency"]),
            days_of_week=[DayOfWeek.from_int(d) for d in data["days_of_week"]],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
        )

    def __str__(self) -> str:
        days_str = ", ".join(d.name.title() for d in self.days_of_week)
        return f"{self.frequency.value.title()} on {days_str}"
