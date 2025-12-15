"""Use case for getting pending instructor profiles for admin review."""

from typing import List, Tuple

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.instructor.value_objects import InstructorStatus
from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository


class GetPendingInstructorsUseCase:
    """
    Use case for getting instructor profiles pending admin review.

    Admin-only use case that retrieves all instructor profiles
    with PENDING_REVIEW status for moderation.
    """

    def __init__(
        self,
        instructor_repo: IInstructorProfileRepository,
        user_repo: IUserRepository,
    ):
        """
        Initialize GetPendingInstructorsUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
            user_repo: Repository for user persistence
        """
        self.instructor_repo = instructor_repo
        self.user_repo = user_repo

    def execute(
        self, skip: int = 0, limit: int = 50
    ) -> List[Tuple[InstructorProfile, User]]:
        """
        Execute the use case to get pending instructor profiles.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of (InstructorProfile, User) tuples for profiles pending review

        Raises:
            RepositoryError: If database operation fails
        """
        # Get pending profiles
        pending_profiles = self.instructor_repo.get_all(
            status=InstructorStatus.PENDING_REVIEW,
            skip=skip,
            limit=limit,
        )

        # Enrich with user data
        results = []
        for profile in pending_profiles:
            user = self.user_repo.get_by_id(profile.user_id)
            if user:
                results.append((profile, user))

        return results
