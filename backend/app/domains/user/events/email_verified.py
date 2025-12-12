"""EmailVerified domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EmailVerified:
    """
    Domain event: User's email has been verified.

    Emitted when user verifies their email address.
    Can trigger:
    - Send confirmation email
    - Activate account features
    - Update user status
    - Log analytics event
    """

    user_id: Optional[int]
    email: str
    verified_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"EmailVerified(user_id={self.user_id}, email={self.email})"
