"""UserProfileUpdated domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserProfileUpdated:
    """
    Domain event: User's profile has been updated.

    Emitted when user updates their profile information.
    Can trigger:
    - Invalidate profile cache
    - Update search index
    - Log activity
    """

    user_id: Optional[int]
    email: str
    updated_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"UserProfileUpdated(user_id={self.user_id}, email={self.email})"
