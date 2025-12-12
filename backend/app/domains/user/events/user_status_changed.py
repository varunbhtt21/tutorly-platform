"""UserStatusChanged domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import UserStatus


@dataclass(frozen=True)
class UserStatusChanged:
    """
    Domain event: User's status has changed.

    Emitted when user status changes (suspended, banned, activated, etc.).
    Can trigger:
    - Send notification email
    - Invalidate sessions (if suspended/banned)
    - Cancel pending bookings (if suspended/banned)
    - Log admin action
    """

    user_id: Optional[int]
    email: str
    old_status: UserStatus
    new_status: UserStatus
    reason: str
    changed_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return (
            f"UserStatusChanged(user_id={self.user_id}, "
            f"{self.old_status} -> {self.new_status})"
        )
