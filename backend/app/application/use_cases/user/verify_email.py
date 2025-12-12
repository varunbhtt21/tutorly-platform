"""Verify email use case."""

from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository


class VerifyEmailUseCase:
    """
    Verify user email use case.

    Orchestrates the email verification process by:
    1. Loading user from repository
    2. Calling domain business logic to verify email
    3. Persisting verified user to repository

    This use case bridges the application layer and domain layer,
    ensuring verification business rules are enforced.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize VerifyEmailUseCase.

        Args:
            user_repo: User repository for persistence
        """
        self.user_repo = user_repo

    def execute(self, user_id: int) -> User:
        """
        Execute email verification.

        This method:
        1. Retrieves user from repository
        2. Calls user.verify_email() domain method
        3. Saves updated user to repository
        4. Returns verified user

        Args:
            user_id: ID of user to verify

        Returns:
            Verified User entity

        Raises:
            ValueError: If user not found or email already verified
        """
        # Get user from repository
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found")

        # Call domain business logic to verify email
        # This method handles validation and emits EmailVerified event
        user.verify_email()

        # Persist updated user to repository
        verified_user = self.user_repo.save(user)

        return verified_user
