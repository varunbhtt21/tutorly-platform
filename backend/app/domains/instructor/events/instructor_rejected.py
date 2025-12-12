"""InstructorRejected domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InstructorRejected:
    """
    Domain event: Instructor profile has been rejected during verification.

    Emitted when an admin rejects an instructor's profile submission.
    Can trigger:
    - Update instructor status back to draft
    - Send rejection notification with reasons
    - Allow instructor to edit and resubmit
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    reason: str
    rejected_by: int
    rejected_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"InstructorRejected(instructor_id={self.instructor_id}, rejected_by={self.rejected_by})"
