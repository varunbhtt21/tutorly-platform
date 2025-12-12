"""BookingSlot domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class SlotStatus(str, Enum):
    """Status of a booking slot."""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"


@dataclass
class BookingSlot:
    """
    Domain entity representing an individual bookable time slot.

    Each BookingSlot is a discrete, bookable unit of time with its own ID.
    This allows individual slot manipulation (resize, delete) without affecting
    other slots from the same availability rule.
    """

    instructor_id: int
    start_at: datetime
    end_at: datetime
    duration_minutes: int = 50
    status: SlotStatus = SlotStatus.AVAILABLE

    # Optional references
    id: Optional[int] = None
    availability_rule_id: Optional[int] = None  # The rule that created this slot
    session_id: Optional[int] = None  # If booked, the session
    timezone: str = "UTC"

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        duration_minutes: int = 50,
        availability_rule_id: Optional[int] = None,
        timezone: str = "UTC",
    ) -> "BookingSlot":
        """
        Factory method to create a new available booking slot.

        Args:
            instructor_id: ID of the instructor
            start_at: Start datetime of the slot
            end_at: End datetime of the slot
            duration_minutes: Duration in minutes
            availability_rule_id: Optional reference to the rule that created this slot
            timezone: Timezone string

        Returns:
            New BookingSlot instance
        """
        return cls(
            instructor_id=instructor_id,
            start_at=start_at,
            end_at=end_at,
            duration_minutes=duration_minutes,
            status=SlotStatus.AVAILABLE,
            availability_rule_id=availability_rule_id,
            timezone=timezone,
            created_at=datetime.utcnow(),
        )

    def book(self, session_id: int) -> None:
        """
        Mark this slot as booked for a session.

        Args:
            session_id: ID of the booked session

        Raises:
            ValueError: If slot is not available
        """
        if self.status != SlotStatus.AVAILABLE:
            raise ValueError(f"Cannot book slot with status '{self.status}'")

        self.status = SlotStatus.BOOKED
        self.session_id = session_id
        self.updated_at = datetime.utcnow()

    def unbook(self) -> None:
        """
        Unbook this slot (cancel the booking).

        Raises:
            ValueError: If slot is not booked
        """
        if self.status != SlotStatus.BOOKED:
            raise ValueError(f"Cannot unbook slot with status '{self.status}'")

        self.status = SlotStatus.AVAILABLE
        self.session_id = None
        self.updated_at = datetime.utcnow()

    def block(self) -> None:
        """
        Block this slot (e.g., due to time off).

        Raises:
            ValueError: If slot is already booked
        """
        if self.status == SlotStatus.BOOKED:
            raise ValueError("Cannot block a booked slot")

        self.status = SlotStatus.BLOCKED
        self.updated_at = datetime.utcnow()

    def unblock(self) -> None:
        """
        Unblock this slot.

        Raises:
            ValueError: If slot is not blocked
        """
        if self.status != SlotStatus.BLOCKED:
            raise ValueError(f"Cannot unblock slot with status '{self.status}'")

        self.status = SlotStatus.AVAILABLE
        self.updated_at = datetime.utcnow()

    def resize(self, new_start_at: datetime, new_end_at: datetime) -> None:
        """
        Resize (extend/shrink) this slot's time window.

        Args:
            new_start_at: New start datetime
            new_end_at: New end datetime

        Raises:
            ValueError: If slot is booked or new times are invalid
        """
        if self.status == SlotStatus.BOOKED:
            raise ValueError("Cannot resize a booked slot")

        if new_end_at <= new_start_at:
            raise ValueError("End time must be after start time")

        self.start_at = new_start_at
        self.end_at = new_end_at
        self.duration_minutes = int((new_end_at - new_start_at).total_seconds() / 60)
        self.updated_at = datetime.utcnow()

    @property
    def is_available(self) -> bool:
        """Check if slot is available for booking."""
        return self.status == SlotStatus.AVAILABLE

    @property
    def is_booked(self) -> bool:
        """Check if slot is booked."""
        return self.status == SlotStatus.BOOKED

    @property
    def is_blocked(self) -> bool:
        """Check if slot is blocked."""
        return self.status == SlotStatus.BLOCKED

    @property
    def date(self) -> str:
        """Get the date of this slot as ISO string."""
        return self.start_at.date().isoformat()

    def overlaps_with(self, start: datetime, end: datetime) -> bool:
        """
        Check if this slot overlaps with a given time range.

        Args:
            start: Start of range to check
            end: End of range to check

        Returns:
            True if there is any overlap
        """
        return self.start_at < end and self.end_at > start
