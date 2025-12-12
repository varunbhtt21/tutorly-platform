"""Use case for completing instructor onboarding."""

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class CompleteInstructorOnboardingUseCase:
    """
    Use case for completing instructor onboarding.

    Marks the instructor profile as fully onboarded after all required steps
    are completed. This validates that all necessary information has been
    provided before allowing the profile to be submitted for review.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize CompleteInstructorOnboardingUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(self, instructor_id: int) -> InstructorProfile:
        """
        Execute the use case to complete onboarding.

        Args:
            instructor_id: Instructor profile ID

        Returns:
            Updated InstructorProfile with onboarding marked as complete

        Raises:
            ValueError: If profile not found
            RepositoryError: If database operation fails
        """
        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # If already complete, just return the profile (idempotent operation)
        if profile.is_onboarding_complete:
            return profile

        # Complete onboarding
        profile.complete_onboarding()

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
