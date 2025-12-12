"""InstructorDashboard read model for dashboard display."""

from dataclasses import dataclass
from typing import List, Any

from ..value_objects import DashboardStats
from .instructor_profile import InstructorProfile
from app.domains.user.entities import User


@dataclass
class InstructorDashboard:
    """
    Aggregate read model for instructor dashboard.

    Combines instructor profile, user info, statistics, and upcoming sessions
    into a single cohesive view for dashboard display.

    This is a read model (not an aggregate root) used specifically for
    efficient dashboard queries and display.
    """

    profile: InstructorProfile
    user: User
    stats: DashboardStats
    upcoming_sessions: List[Any]  # Placeholder for future Session entities

    @property
    def is_profile_complete(self) -> bool:
        """Check if instructor profile onboarding is complete."""
        return self.profile.is_onboarding_complete

    @property
    def can_accept_bookings(self) -> bool:
        """Check if instructor can accept bookings."""
        return self.profile.can_accept_bookings

    @property
    def is_verified(self) -> bool:
        """Check if instructor is verified."""
        return self.profile.is_verified

    @property
    def full_name(self) -> str:
        """Get instructor's full name from user."""
        return self.user.full_name

    @property
    def has_upcoming_sessions(self) -> bool:
        """Check if instructor has upcoming sessions."""
        return len(self.upcoming_sessions) > 0

    @property
    def profile_completion_percent(self) -> int:
        """Get profile completion percentage."""
        return self.stats.profile_completion_percent

    def __str__(self) -> str:
        """String representation."""
        return (
            f"InstructorDashboard("
            f"user={self.full_name}, "
            f"status={self.profile.status.value}, "
            f"complete={self.is_profile_complete})"
        )
