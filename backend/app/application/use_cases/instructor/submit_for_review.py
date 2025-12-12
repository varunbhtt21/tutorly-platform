"""Use case for submitting instructor profile for review."""

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class SubmitForReviewUseCase:
    """
    Use case for submitting instructor profile for review.

    Submits a completed instructor profile to the admin verification queue.
    This transitions the profile from DRAFT status to PENDING_REVIEW status,
    making it available for admin review and verification.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize SubmitForReviewUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(self, instructor_id: int) -> InstructorProfile:
        """
        Execute the use case to submit profile for review.

        Args:
            instructor_id: Instructor profile ID

        Returns:
            Updated InstructorProfile with PENDING_REVIEW status

        Raises:
            ValueError: If profile not found, onboarding incomplete, or
                       profile cannot be submitted in current status
            RepositoryError: If database operation fails
        """
        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # Submit for review (validates onboarding complete and status)
        profile.submit_for_review()

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
