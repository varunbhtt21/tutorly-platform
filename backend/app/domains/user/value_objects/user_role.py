"""UserRole value object."""

from enum import Enum


class UserRole(str, Enum):
    """
    User role enumeration.

    Defines the primary role/type of user in the system.
    """

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

    def __str__(self) -> str:
        """String representation."""
        return self.value

    @property
    def is_student(self) -> bool:
        """Check if role is student."""
        return self == UserRole.STUDENT

    @property
    def is_instructor(self) -> bool:
        """Check if role is instructor."""
        return self == UserRole.INSTRUCTOR

    @property
    def is_admin(self) -> bool:
        """Check if role is admin."""
        return self == UserRole.ADMIN

    def can_teach(self) -> bool:
        """Check if role can teach (create sessions, etc.)."""
        return self in (UserRole.INSTRUCTOR, UserRole.ADMIN)

    def can_learn(self) -> bool:
        """Check if role can learn (book sessions, etc.)."""
        return self in (UserRole.STUDENT, UserRole.ADMIN)

    def has_admin_privileges(self) -> bool:
        """Check if role has admin privileges."""
        return self == UserRole.ADMIN
