"""TimeSlot value object for scheduling domain."""

from dataclasses import dataclass
from datetime import time, datetime, timedelta
from typing import List


@dataclass(frozen=True)
class TimeSlot:
    """
    Immutable value object representing a time range.

    Used for both availability windows and session times.
    """
    start_time: time
    end_time: time

    def __post_init__(self):
        """Validate the time slot."""
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")

    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        start_dt = datetime.combine(datetime.min, self.start_time)
        end_dt = datetime.combine(datetime.min, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)

    def overlaps(self, other: "TimeSlot") -> bool:
        """Check if this time slot overlaps with another."""
        return self.start_time < other.end_time and self.end_time > other.start_time

    def contains(self, other: "TimeSlot") -> bool:
        """Check if this time slot fully contains another."""
        return self.start_time <= other.start_time and self.end_time >= other.end_time

    def generate_slots(
        self,
        slot_duration_minutes: int = 50,
        break_minutes: int = 10
    ) -> List["TimeSlot"]:
        """
        Generate individual bookable slots within this time window.

        Args:
            slot_duration_minutes: Duration of each slot (default 50 min)
            break_minutes: Break between slots (default 10 min)

        Returns:
            List of TimeSlot objects representing bookable slots
        """
        slots = []
        total_slot_minutes = slot_duration_minutes + break_minutes

        current_start = datetime.combine(datetime.min, self.start_time)
        end = datetime.combine(datetime.min, self.end_time)

        while True:
            slot_end = current_start + timedelta(minutes=slot_duration_minutes)
            if slot_end > end:
                break

            slots.append(TimeSlot(
                start_time=current_start.time(),
                end_time=slot_end.time()
            ))

            current_start = current_start + timedelta(minutes=total_slot_minutes)

        return slots

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": self.duration_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimeSlot":
        """Create from dictionary."""
        return cls(
            start_time=time.fromisoformat(data["start_time"]),
            end_time=time.fromisoformat(data["end_time"]),
        )

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
