"""PasswordChanged domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PasswordChanged:
    """
    Domain event: User's password has been changed.

    Emitted when user changes their password.
    Can trigger:
    - Send security notification email
    - Invalidate all sessions
    - Log security event
    """

    user_id: Optional[int]
    email: str
    changed_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"PasswordChanged(user_id={self.user_id}, email={self.email})"
