"""SessionType value object for scheduling domain."""

from enum import Enum


class SessionType(Enum):
    """Type of tutoring session."""
    TRIAL = "trial"
    SINGLE = "single"
    RECURRING = "recurring"

    @property
    def is_trial(self) -> bool:
        """Check if this is a trial session."""
        return self == SessionType.TRIAL

    @property
    def is_recurring(self) -> bool:
        """Check if this is a recurring session."""
        return self == SessionType.RECURRING

    @classmethod
    def from_string(cls, value: str) -> "SessionType":
        """Create from string value."""
        return cls(value.lower())
