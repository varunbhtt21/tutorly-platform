"""AvailabilityType value object for scheduling domain."""

from enum import Enum


class AvailabilityType(Enum):
    """Type of availability slot."""
    RECURRING = "recurring"  # Repeats weekly on specific days
    ONE_TIME = "one_time"    # Single specific date

    @property
    def is_recurring(self) -> bool:
        """Check if this is a recurring availability."""
        return self == AvailabilityType.RECURRING

    @classmethod
    def from_string(cls, value: str) -> "AvailabilityType":
        """Create from string value."""
        return cls(value.lower())
