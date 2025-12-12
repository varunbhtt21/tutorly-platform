"""Use case for verifying instructor profile (admin action)."""

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class VerifyInstructorUseCase:
    """
    Use case for verifying instructor profile (admin action).

    Admin-only use case that verifies an instructor profile after review.
    This transitions the profile from PENDING_REVIEW to VERIFIED status,
    making it visible to students and allowing the instructor to accept
    bookings.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize VerifyInstructorUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(self, instructor_id: int, verified_by_admin_id: int) -> InstructorProfile:
        """
        Execute the use case to verify instructor profile.

        Args:
            instructor_id: Instructor profile ID
            verified_by_admin_id: ID of admin who is verifying

        Returns:
            Updated InstructorProfile with VERIFIED status

        Raises:
            ValueError: If profile not found or cannot be verified in
                       current status
            RepositoryError: If database operation fails
        """
        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # Verify profile (validates status allows verification)
        profile.verify(verified_by_admin_id)

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
