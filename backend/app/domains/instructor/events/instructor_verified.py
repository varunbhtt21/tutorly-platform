"""InstructorVerified domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InstructorVerified:
    """
    Domain event: Instructor profile has been verified and approved.

    Emitted when an admin approves an instructor's profile for publication.
    Can trigger:
    - Update instructor status to verified
    - Make instructor visible to students in search
    - Send approval notification email
    - Enable booking functionality
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    verified_by: int
    verified_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"InstructorVerified(instructor_id={self.instructor_id}, verified_by={self.verified_by})"
