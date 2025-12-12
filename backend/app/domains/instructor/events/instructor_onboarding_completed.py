"""InstructorOnboardingCompleted domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InstructorOnboardingCompleted:
    """
    Domain event: Instructor has completed all onboarding steps.

    Emitted when an instructor successfully completes the entire onboarding process.
    Can trigger:
    - Submit profile for verification
    - Send completion confirmation email
    - Update instructor status to pending verification
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    completed_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"InstructorOnboardingCompleted(instructor_id={self.instructor_id}, user_id={self.user_id})"
