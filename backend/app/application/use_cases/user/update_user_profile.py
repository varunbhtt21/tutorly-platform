"""Update user profile use case."""

from typing import Optional
from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository


class UpdateUserProfileUseCase:
    """
    Update user profile use case.

    Orchestrates the profile update process by:
    1. Loading user from repository
    2. Calling domain business logic to update profile
    3. Persisting updated user to repository

    This use case bridges the application layer and domain layer,
    ensuring profile updates are properly validated and tracked
    with domain events.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize UpdateUserProfileUseCase.

        Args:
            user_repo: User repository for persistence
        """
        self.user_repo = user_repo

    def execute(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> User:
        """
        Execute user profile update.

        This method:
        1. Retrieves user from repository
        2. Calls user.update_profile() domain method with provided fields
        3. Saves updated user to repository
        4. Returns updated user

        Only provided fields (non-None) are updated. Fields left as None
        remain unchanged. The domain method ensures only actual changes
        are saved and only emits event if something changed.

        Args:
            user_id: ID of user to update
            first_name: Optional new first name
            last_name: Optional new last name
            phone_number: Optional new phone number

        Returns:
            Updated User entity

        Raises:
            ValueError: If user not found
        """
        # Get user from repository
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found")

        # Call domain business logic to update profile
        # Only updates fields that are provided and different from current values
        # Emits UserProfileUpdated event only if something actually changed
        user.update_profile(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        # Persist updated user to repository
        updated_user = self.user_repo.save(user)

        return updated_user
