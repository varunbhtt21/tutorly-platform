"""InstructorOnboardingStarted domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class InstructorOnboardingStarted:
    """
    Domain event: Instructor has started the onboarding process.

    Emitted when an instructor begins their onboarding workflow.
    Can trigger:
    - Initialize onboarding progress tracking
    - Send onboarding instructions
    - Log analytics event
    """

    user_id: int
    instructor_id: Optional[int]
    started_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"InstructorOnboardingStarted(user_id={self.user_id}, instructor_id={self.instructor_id})"
