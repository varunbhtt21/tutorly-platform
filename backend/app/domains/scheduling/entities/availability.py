"""Availability entity for scheduling domain."""

from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import Optional, List

from ..value_objects import (
    AvailabilityType,
    TimeSlot,
    DayOfWeek,
)


@dataclass
class Availability:
    """
    Aggregate root representing an instructor's availability.

    Handles both recurring weekly availability and one-time slots.
    """
    instructor_id: int
    availability_type: AvailabilityType
    start_time: time
    end_time: time
    timezone: str = "UTC"
    slot_duration_minutes: int = 50
    break_minutes: int = 10
    is_active: bool = True

    # For recurring availability
    day_of_week: Optional[DayOfWeek] = None

    # For one-time availability
    specific_date: Optional[date] = None

    # Validity period (for recurring)
    valid_from: date = field(default_factory=date.today)
    valid_until: Optional[date] = None

    # Identity
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate availability after initialization."""
        self._validate()

    def _validate(self):
        """Validate availability configuration."""
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")

        if self.availability_type == AvailabilityType.RECURRING:
            if self.day_of_week is None:
                raise ValueError("Recurring availability requires day_of_week")
        else:  # ONE_TIME
            if self.specific_date is None:
                raise ValueError("One-time availability requires specific_date")

        if self.slot_duration_minutes < 15:
            raise ValueError("Slot duration must be at least 15 minutes")

        if self.break_minutes < 0:
            raise ValueError("Break time cannot be negative")

    @property
    def time_slot(self) -> TimeSlot:
        """Get the time slot for this availability."""
        return TimeSlot(start_time=self.start_time, end_time=self.end_time)

    @property
    def is_recurring(self) -> bool:
        """Check if this is recurring availability."""
        return self.availability_type == AvailabilityType.RECURRING

    def is_valid_on(self, check_date: date) -> bool:
        """Check if availability is valid on a specific date."""
        if not self.is_active:
            return False

        if check_date < self.valid_from:
            return False

        if self.valid_until and check_date > self.valid_until:
            return False

        if self.is_recurring:
            # Check if the day of week matches
            return check_date.weekday() == self.day_of_week.value
        else:
            # Check if specific date matches
            return check_date == self.specific_date

    def generate_slots_for_date(self, target_date: date) -> List[dict]:
        """
        Generate bookable time slots for a specific date.

        Returns list of slot dictionaries with start/end times.
        """
        if not self.is_valid_on(target_date):
            return []

        slots = self.time_slot.generate_slots(
            slot_duration_minutes=self.slot_duration_minutes,
            break_minutes=self.break_minutes
        )

        return [
            {
                "date": target_date.isoformat(),
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "start_datetime": datetime.combine(target_date, slot.start_time).isoformat(),
                "end_datetime": datetime.combine(target_date, slot.end_time).isoformat(),
                "duration_minutes": self.slot_duration_minutes,
                "availability_id": self.id,
            }
            for slot in slots
        ]

    def deactivate(self):
        """Deactivate this availability."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate this availability."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_time_window(self, start_time: time, end_time: time):
        """Update the time window."""
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        self.start_time = start_time
        self.end_time = end_time
        self.updated_at = datetime.utcnow()

    def update_slot_config(self, duration_minutes: int, break_minutes: int):
        """Update slot configuration."""
        if duration_minutes < 15:
            raise ValueError("Slot duration must be at least 15 minutes")
        if break_minutes < 0:
            raise ValueError("Break time cannot be negative")
        self.slot_duration_minutes = duration_minutes
        self.break_minutes = break_minutes
        self.updated_at = datetime.utcnow()

    def set_validity_period(self, valid_from: date, valid_until: Optional[date]):
        """Set the validity period."""
        if valid_until and valid_until < valid_from:
            raise ValueError("Valid until must be after valid from")
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.updated_at = datetime.utcnow()

    @classmethod
    def create_recurring(
        cls,
        instructor_id: int,
        day_of_week: DayOfWeek,
        start_time: time,
        end_time: time,
        timezone: str = "UTC",
        slot_duration_minutes: int = 50,
        break_minutes: int = 10,
        valid_from: Optional[date] = None,
        valid_until: Optional[date] = None,
    ) -> "Availability":
        """Factory method for creating recurring availability."""
        return cls(
            instructor_id=instructor_id,
            availability_type=AvailabilityType.RECURRING,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            slot_duration_minutes=slot_duration_minutes,
            break_minutes=break_minutes,
            valid_from=valid_from or date.today(),
            valid_until=valid_until,
        )

    @classmethod
    def create_one_time(
        cls,
        instructor_id: int,
        specific_date: date,
        start_time: time,
        end_time: time,
        timezone: str = "UTC",
        slot_duration_minutes: int = 50,
        break_minutes: int = 10,
    ) -> "Availability":
        """Factory method for creating one-time availability."""
        return cls(
            instructor_id=instructor_id,
            availability_type=AvailabilityType.ONE_TIME,
            specific_date=specific_date,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            slot_duration_minutes=slot_duration_minutes,
            break_minutes=break_minutes,
            valid_from=specific_date,
            valid_until=specific_date,
        )

    def __repr__(self) -> str:
        if self.is_recurring:
            return f"Availability(recurring, {self.day_of_week.name}, {self.start_time}-{self.end_time})"
        return f"Availability(one-time, {self.specific_date}, {self.start_time}-{self.end_time})"
