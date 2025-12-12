"""Use case for creating instructor profile."""

from typing import Optional

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class CreateInstructorProfileUseCase:
    """
    Use case for creating a new instructor profile.

    Creates an instructor profile for a user who is transitioning to become
    an instructor. Initializes the profile in DRAFT status with default
    onboarding state.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize CreateInstructorProfileUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(self, user_id: int) -> InstructorProfile:
        """
        Execute the use case to create instructor profile.

        Args:
            user_id: User ID who is becoming an instructor

        Returns:
            Created InstructorProfile with ID populated

        Raises:
            ValueError: If user already has an instructor profile
            RepositoryError: If database operation fails
        """
        # Check if profile already exists
        existing_profile = self.instructor_repo.get_by_user_id(user_id)
        if existing_profile:
            raise ValueError(f"Instructor profile already exists for user {user_id}")

        # Create new profile using factory method
        profile = InstructorProfile.create_for_user(user_id)

        # Save to repository
        saved_profile = self.instructor_repo.save(profile)

        return saved_profile
