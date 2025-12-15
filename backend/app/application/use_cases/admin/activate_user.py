"""Use case for activating user account (admin action)."""

from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository


class ActivateUserUseCase:
    """
    Use case for activating user account (admin action).

    Admin-only use case that activates a suspended or inactive user account.
    This transitions the account to ACTIVE status,
    allowing the user to log in again.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize ActivateUserUseCase.

        Args:
            user_repo: Repository for user persistence
        """
        self.user_repo = user_repo

    def execute(self, user_id: int) -> User:
        """
        Execute the use case to activate user account.

        Args:
            user_id: User ID to activate

        Returns:
            Updated User with ACTIVE status

        Raises:
            ValueError: If user not found or cannot be activated
            RepositoryError: If database operation fails
        """
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Activate user (validates status allows activation)
        user.activate()

        # Save updated user
        updated_user = self.user_repo.update(user)

        return updated_user
