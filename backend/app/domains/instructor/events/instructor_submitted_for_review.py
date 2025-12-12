"""InstructorSubmittedForReview domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InstructorSubmittedForReview:
    """
    Domain event: Instructor profile has been submitted for verification review.

    Emitted when an instructor submits their completed profile for admin review.
    Can trigger:
    - Create verification request record
    - Update instructor status to pending verification
    - Notify admin of new verification request
    - Send confirmation email to instructor
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    submitted_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"InstructorSubmittedForReview(instructor_id={self.instructor_id}, user_id={self.user_id})"
