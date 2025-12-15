"""Use case for suspending user account (admin action)."""

from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository


class SuspendUserUseCase:
    """
    Use case for suspending user account (admin action).

    Admin-only use case that suspends a user account.
    This transitions the account from ACTIVE to SUSPENDED status,
    preventing the user from logging in.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize SuspendUserUseCase.

        Args:
            user_repo: Repository for user persistence
        """
        self.user_repo = user_repo

    def execute(self, user_id: int, reason: str) -> User:
        """
        Execute the use case to suspend user account.

        Args:
            user_id: User ID to suspend
            reason: Reason for suspension

        Returns:
            Updated User with SUSPENDED status

        Raises:
            ValueError: If user not found, reason empty, or cannot be suspended
            RepositoryError: If database operation fails
        """
        if not reason or not reason.strip():
            raise ValueError("Suspension reason is required")

        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Cannot suspend admins
        if user.is_admin:
            raise ValueError("Cannot suspend admin users")

        # Suspend user (validates status allows suspension)
        user.suspend(reason.strip())

        # Save updated user
        updated_user = self.user_repo.update(user)

        return updated_user
