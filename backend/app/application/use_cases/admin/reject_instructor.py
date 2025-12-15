"""Use case for rejecting instructor profile (admin action)."""

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class RejectInstructorUseCase:
    """
    Use case for rejecting instructor profile (admin action).

    Admin-only use case that rejects an instructor profile after review.
    This transitions the profile from PENDING_REVIEW to REJECTED status.
    The instructor can update their profile and resubmit for review.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize RejectInstructorUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(
        self, instructor_id: int, reason: str, rejected_by_admin_id: int
    ) -> InstructorProfile:
        """
        Execute the use case to reject instructor profile.

        Args:
            instructor_id: Instructor profile ID
            reason: Reason for rejection (shown to instructor)
            rejected_by_admin_id: ID of admin who is rejecting

        Returns:
            Updated InstructorProfile with REJECTED status

        Raises:
            ValueError: If profile not found, reason empty, or cannot be rejected
            RepositoryError: If database operation fails
        """
        if not reason or not reason.strip():
            raise ValueError("Rejection reason is required")

        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # Reject profile (validates status allows rejection)
        profile.reject(reason.strip(), rejected_by_admin_id)

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
