"""Use case for getting admin dashboard statistics."""

from dataclasses import dataclass

from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.instructor.value_objects import InstructorStatus
from app.domains.user.repositories import IUserRepository
from app.domains.user.value_objects import UserRole, UserStatus


@dataclass
class AdminDashboardStats:
    """Admin dashboard statistics."""

    # User counts
    total_users: int
    total_students: int
    total_instructors: int
    total_admins: int

    # User status counts
    active_users: int
    suspended_users: int
    banned_users: int

    # Instructor status counts
    pending_instructors: int
    verified_instructors: int
    rejected_instructors: int
    suspended_instructors: int


class GetAdminDashboardStatsUseCase:
    """
    Use case for getting admin dashboard statistics.

    Admin-only use case that retrieves platform statistics
    for the admin dashboard.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        instructor_repo: IInstructorProfileRepository,
    ):
        """
        Initialize GetAdminDashboardStatsUseCase.

        Args:
            user_repo: Repository for user persistence
            instructor_repo: Repository for instructor profile persistence
        """
        self.user_repo = user_repo
        self.instructor_repo = instructor_repo

    def execute(self) -> AdminDashboardStats:
        """
        Execute the use case to get admin dashboard statistics.

        Returns:
            AdminDashboardStats with platform statistics

        Raises:
            RepositoryError: If database operation fails
        """
        # User counts by role
        total_users = self.user_repo.count()
        total_students = self.user_repo.count(role=UserRole.STUDENT)
        total_instructors = self.user_repo.count(role=UserRole.INSTRUCTOR)
        total_admins = self.user_repo.count(role=UserRole.ADMIN)

        # User counts by status
        active_users = self.user_repo.count(status=UserStatus.ACTIVE)
        suspended_users = self.user_repo.count(status=UserStatus.SUSPENDED)
        banned_users = self.user_repo.count(status=UserStatus.BANNED)

        # Instructor counts by status
        pending_instructors = self.instructor_repo.count(
            status=InstructorStatus.PENDING_REVIEW
        )
        verified_instructors = self.instructor_repo.count(
            status=InstructorStatus.VERIFIED
        )
        rejected_instructors = self.instructor_repo.count(
            status=InstructorStatus.REJECTED
        )
        suspended_instructors = self.instructor_repo.count(
            status=InstructorStatus.SUSPENDED
        )

        return AdminDashboardStats(
            total_users=total_users,
            total_students=total_students,
            total_instructors=total_instructors,
            total_admins=total_admins,
            active_users=active_users,
            suspended_users=suspended_users,
            banned_users=banned_users,
            pending_instructors=pending_instructors,
            verified_instructors=verified_instructors,
            rejected_instructors=rejected_instructors,
            suspended_instructors=suspended_instructors,
        )
