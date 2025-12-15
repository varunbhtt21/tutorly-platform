"""Use case for suspending instructor profile (admin action)."""

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class SuspendInstructorUseCase:
    """
    Use case for suspending instructor profile (admin action).

    Admin-only use case that suspends a verified instructor.
    This transitions the profile from VERIFIED to SUSPENDED status,
    preventing the instructor from accepting new bookings.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize SuspendInstructorUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(
        self, instructor_id: int, reason: str, suspended_by_admin_id: int
    ) -> InstructorProfile:
        """
        Execute the use case to suspend instructor profile.

        Args:
            instructor_id: Instructor profile ID
            reason: Reason for suspension
            suspended_by_admin_id: ID of admin who is suspending

        Returns:
            Updated InstructorProfile with SUSPENDED status

        Raises:
            ValueError: If profile not found, reason empty, or cannot be suspended
            RepositoryError: If database operation fails
        """
        if not reason or not reason.strip():
            raise ValueError("Suspension reason is required")

        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # Suspend profile (validates status allows suspension)
        profile.suspend(reason.strip(), suspended_by_admin_id)

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
