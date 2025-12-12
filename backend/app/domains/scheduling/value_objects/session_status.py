"""SessionStatus value object for scheduling domain."""

from enum import Enum


class SessionStatus(Enum):
    """Status of a tutoring session."""
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

    @property
    def is_active(self) -> bool:
        """Check if session is in an active state (not cancelled/completed)."""
        return self in (
            SessionStatus.PENDING_CONFIRMATION,
            SessionStatus.CONFIRMED,
            SessionStatus.IN_PROGRESS,
        )

    @property
    def is_final(self) -> bool:
        """Check if session is in a final state."""
        return self in (
            SessionStatus.COMPLETED,
            SessionStatus.CANCELLED,
            SessionStatus.NO_SHOW,
        )

    @property
    def can_be_cancelled(self) -> bool:
        """Check if session can be cancelled."""
        return self in (
            SessionStatus.PENDING_CONFIRMATION,
            SessionStatus.CONFIRMED,
        )

    @property
    def can_be_rescheduled(self) -> bool:
        """Check if session can be rescheduled."""
        return self in (
            SessionStatus.PENDING_CONFIRMATION,
            SessionStatus.CONFIRMED,
        )

    @classmethod
    def from_string(cls, value: str) -> "SessionStatus":
        """Create from string value."""
        return cls(value.lower())
