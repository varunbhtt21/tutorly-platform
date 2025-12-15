"""AdminActionPerformed domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import AdminAction


@dataclass(frozen=True)
class AdminActionPerformed:
    """
    Domain event emitted when an admin performs an action.

    Captures audit trail for all admin moderation actions.
    """

    admin_id: int
    action: AdminAction
    target_type: str  # "instructor" or "user"
    target_id: int
    reason: Optional[str]
    performed_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return (
            f"AdminActionPerformed("
            f"admin={self.admin_id}, "
            f"action={self.action}, "
            f"target={self.target_type}:{self.target_id})"
        )
