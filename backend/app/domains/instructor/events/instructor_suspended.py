"""InstructorSuspended domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InstructorSuspended:
    """
    Domain event: Instructor account has been suspended.

    Emitted when an admin temporarily suspends an instructor's account.
    Can trigger:
    - Update instructor status to suspended
    - Hide instructor from student search
    - Cancel or postpone upcoming sessions
    - Send suspension notification with reason
    - Lock instructor from accepting new bookings
    - Log audit trail
    """

    instructor_id: int
    user_id: int
    reason: str
    suspended_by: int
    suspended_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"InstructorSuspended(instructor_id={self.instructor_id}, suspended_by={self.suspended_by})"
