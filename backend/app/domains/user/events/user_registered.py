"""UserRegistered domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import UserRole


@dataclass(frozen=True)
class UserRegistered:
    """
    Domain event: User has registered.

    Emitted when a new user successfully registers.
    Can trigger:
    - Send welcome email
    - Send email verification
    - Create initial preferences
    - Log analytics event
    """

    user_id: Optional[int]
    email: str
    role: UserRole
    registered_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"UserRegistered(user_id={self.user_id}, email={self.email}, role={self.role})"
