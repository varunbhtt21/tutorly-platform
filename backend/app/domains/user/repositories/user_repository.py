"""User repository interface (Port)."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import User
from ..value_objects import Email, UserRole, UserStatus


class IUserRepository(ABC):
    """
    User repository interface.

    Defines the contract for user persistence.
    Implementation will be in Infrastructure layer (adapter).

    Following Hexagonal Architecture:
    - This is a PORT (interface in domain)
    - Infrastructure provides ADAPTER (SQLAlchemy implementation)
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Save user to persistence.

        Args:
            user: User entity

        Returns:
            Saved user with ID
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    def email_exists(self, email: Email) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        pass

    @abstractmethod
    def get_all(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Get all users with optional filtering.

        Args:
            role: Filter by role
            status: Filter by status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """
        Update existing user.

        Args:
            user: User entity with changes

        Returns:
            Updated user
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Delete user (hard delete).

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def count(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
    ) -> int:
        """
        Count users with optional filtering.

        Args:
            role: Filter by role
            status: Filter by status

        Returns:
            Number of users matching criteria
        """
        pass
