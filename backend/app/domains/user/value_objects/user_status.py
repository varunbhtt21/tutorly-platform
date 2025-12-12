"""UserStatus value object."""

from enum import Enum


class UserStatus(str, Enum):
    """
    User account status enumeration.

    Defines the current state of a user account.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"

    def __str__(self) -> str:
        """String representation."""
        return self.value

    @property
    def is_active(self) -> bool:
        """Check if status is active."""
        return self == UserStatus.ACTIVE

    @property
    def is_deleted(self) -> bool:
        """Check if status is deleted."""
        return self == UserStatus.DELETED

    @property
    def is_suspended(self) -> bool:
        """Check if status is suspended."""
        return self == UserStatus.SUSPENDED

    @property
    def is_banned(self) -> bool:
        """Check if status is banned."""
        return self == UserStatus.BANNED

    def can_login(self) -> bool:
        """Check if user can login with this status."""
        return self in (UserStatus.ACTIVE, UserStatus.INACTIVE)

    def can_be_activated(self) -> bool:
        """Check if status can be changed to active."""
        return self in (UserStatus.INACTIVE, UserStatus.SUSPENDED)

    def requires_verification(self) -> bool:
        """Check if status requires email verification."""
        return self == UserStatus.INACTIVE
