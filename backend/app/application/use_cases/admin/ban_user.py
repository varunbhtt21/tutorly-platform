"""Use case for banning user account (admin action)."""

from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository


class BanUserUseCase:
    """
    Use case for banning user account (admin action).

    Admin-only use case that permanently bans a user account.
    This transitions the account to BANNED status,
    preventing the user from ever logging in again.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize BanUserUseCase.

        Args:
            user_repo: Repository for user persistence
        """
        self.user_repo = user_repo

    def execute(self, user_id: int, reason: str) -> User:
        """
        Execute the use case to ban user account.

        Args:
            user_id: User ID to ban
            reason: Reason for ban

        Returns:
            Updated User with BANNED status

        Raises:
            ValueError: If user not found, reason empty, or cannot be banned
            RepositoryError: If database operation fails
        """
        if not reason or not reason.strip():
            raise ValueError("Ban reason is required")

        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Cannot ban admins
        if user.is_admin:
            raise ValueError("Cannot ban admin users")

        # Ban user (validates status allows banning)
        user.ban(reason.strip())

        # Save updated user
        updated_user = self.user_repo.update(user)

        return updated_user
