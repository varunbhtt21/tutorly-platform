"""AdminAction value object."""

from enum import Enum


class AdminAction(str, Enum):
    """
    Admin action enumeration.

    Represents the types of moderation actions an admin can perform.
    """

    # Instructor actions
    VERIFY_INSTRUCTOR = "verify_instructor"
    REJECT_INSTRUCTOR = "reject_instructor"
    SUSPEND_INSTRUCTOR = "suspend_instructor"
    REACTIVATE_INSTRUCTOR = "reactivate_instructor"

    # User actions
    SUSPEND_USER = "suspend_user"
    BAN_USER = "ban_user"
    ACTIVATE_USER = "activate_user"

    def __str__(self) -> str:
        """String representation."""
        return self.value

    @property
    def is_instructor_action(self) -> bool:
        """Check if action is for instructor management."""
        return self in (
            AdminAction.VERIFY_INSTRUCTOR,
            AdminAction.REJECT_INSTRUCTOR,
            AdminAction.SUSPEND_INSTRUCTOR,
            AdminAction.REACTIVATE_INSTRUCTOR,
        )

    @property
    def is_user_action(self) -> bool:
        """Check if action is for user management."""
        return self in (
            AdminAction.SUSPEND_USER,
            AdminAction.BAN_USER,
            AdminAction.ACTIVATE_USER,
        )

    @property
    def display_name(self) -> str:
        """Get human-readable display name."""
        display_names = {
            AdminAction.VERIFY_INSTRUCTOR: "Verify Instructor",
            AdminAction.REJECT_INSTRUCTOR: "Reject Instructor",
            AdminAction.SUSPEND_INSTRUCTOR: "Suspend Instructor",
            AdminAction.REACTIVATE_INSTRUCTOR: "Reactivate Instructor",
            AdminAction.SUSPEND_USER: "Suspend User",
            AdminAction.BAN_USER: "Ban User",
            AdminAction.ACTIVATE_USER: "Activate User",
        }
        return display_names.get(self, self.value)
