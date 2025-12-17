"""Use case for getting instructor dashboard data."""

from decimal import Decimal
from typing import Optional

from app.domains.instructor.entities import InstructorProfile, InstructorDashboard
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.instructor.value_objects import DashboardStats
from app.domains.wallet.repositories import IWalletRepository


class GetInstructorDashboardUseCase:
    """
    Use case for retrieving instructor dashboard data.

    Orchestrates fetching instructor profile, user data, and calculating
    statistics for dashboard display.
    """

    def __init__(
        self,
        instructor_repo: IInstructorProfileRepository,
        wallet_repo: Optional[IWalletRepository] = None,
    ):
        """
        Initialize GetInstructorDashboardUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
            wallet_repo: Optional wallet repository for earnings data
        """
        self.instructor_repo = instructor_repo
        self.wallet_repo = wallet_repo

    def execute(self, user_id: int) -> InstructorDashboard:
        """
        Execute the use case to get instructor dashboard data.

        Args:
            user_id: The authenticated instructor's user ID

        Returns:
            InstructorDashboard: Aggregated dashboard data

        Raises:
            ValueError: If instructor profile not found
        """
        # 1. Fetch profile with user data
        result = self.instructor_repo.get_dashboard_data(user_id)
        if not result:
            raise ValueError(f"Instructor profile not found for user {user_id}")

        profile, user = result

        # 2. Calculate profile completion percentage
        completion = self._calculate_profile_completion(profile)

        # 3. Get wallet earnings if wallet_repo is provided
        total_earnings = Decimal("0.00")
        if self.wallet_repo:
            wallet = self.wallet_repo.get_by_instructor_id(profile.id)
            if wallet:
                total_earnings = wallet.total_earned

        # 4. Build stats (uses existing profile data + wallet earnings)
        stats = DashboardStats(
            upcoming_sessions_count=0,  # Placeholder until session system
            total_students=0,  # Placeholder until booking system
            completed_sessions=profile.total_sessions_completed,
            total_earnings=total_earnings,
            profile_completion_percent=completion,
        )

        # 5. Return dashboard aggregate
        return InstructorDashboard(
            profile=profile,
            user=user,
            stats=stats,
            upcoming_sessions=[],  # Placeholder until session system
        )

    def _calculate_profile_completion(self, profile: InstructorProfile) -> int:
        """
        Calculate profile completion as percentage.

        Args:
            profile: Instructor profile to evaluate

        Returns:
            int: Completion percentage (0-100)
        """
        required_fields = [
            profile.country_of_birth,
            profile.languages_spoken,
            profile.profile_photo_url,
            profile.bio,
            profile.teaching_experience,
            profile.headline,
            profile.intro_video_url,
            profile.pricing,
        ]
        completed = sum(1 for field in required_fields if field)
        return int((completed / len(required_fields)) * 100)
