"""DashboardStats value object for instructor dashboard."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DashboardStats:
    """
    Immutable value object representing instructor dashboard statistics.

    Read-only snapshot of aggregated instructor data for dashboard display.
    """

    upcoming_sessions_count: int
    total_students: int
    completed_sessions: int
    total_earnings: Decimal
    profile_completion_percent: int

    def __post_init__(self):
        """Validate stats on creation."""
        if self.upcoming_sessions_count < 0:
            raise ValueError("Upcoming sessions count cannot be negative")
        if self.total_students < 0:
            raise ValueError("Total students cannot be negative")
        if self.completed_sessions < 0:
            raise ValueError("Completed sessions cannot be negative")
        if self.total_earnings < 0:
            raise ValueError("Total earnings cannot be negative")
        if not 0 <= self.profile_completion_percent <= 100:
            raise ValueError("Profile completion must be between 0 and 100")

    @classmethod
    def create_empty(cls) -> "DashboardStats":
        """
        Factory for new instructors with no activity.

        Returns:
            DashboardStats with all zeros
        """
        return cls(
            upcoming_sessions_count=0,
            total_students=0,
            completed_sessions=0,
            total_earnings=Decimal("0.00"),
            profile_completion_percent=0,
        )

    @classmethod
    def create(
        cls,
        upcoming_sessions_count: int,
        total_students: int,
        completed_sessions: int,
        total_earnings: float,
        profile_completion_percent: int,
    ) -> "DashboardStats":
        """
        Create DashboardStats from primitive values.

        Args:
            upcoming_sessions_count: Number of upcoming sessions
            total_students: Total number of students taught
            completed_sessions: Number of completed sessions
            total_earnings: Total earnings in dollars
            profile_completion_percent: Profile completion percentage (0-100)

        Returns:
            DashboardStats instance
        """
        return cls(
            upcoming_sessions_count=upcoming_sessions_count,
            total_students=total_students,
            completed_sessions=completed_sessions,
            total_earnings=Decimal(str(total_earnings)),
            profile_completion_percent=profile_completion_percent,
        )

    @property
    def earnings_float(self) -> float:
        """Get total earnings as float for JSON serialization."""
        return float(self.total_earnings)

    @property
    def has_activity(self) -> bool:
        """Check if instructor has any teaching activity."""
        return self.completed_sessions > 0 or self.total_students > 0

    @property
    def has_upcoming_sessions(self) -> bool:
        """Check if instructor has upcoming sessions."""
        return self.upcoming_sessions_count > 0

    def __str__(self) -> str:
        """String representation."""
        return (
            f"DashboardStats("
            f"sessions={self.completed_sessions}, "
            f"students={self.total_students}, "
            f"earnings=${self.earnings_float:.2f}, "
            f"completion={self.profile_completion_percent}%)"
        )

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, DashboardStats):
            return (
                self.upcoming_sessions_count == other.upcoming_sessions_count
                and self.total_students == other.total_students
                and self.completed_sessions == other.completed_sessions
                and self.total_earnings == other.total_earnings
                and self.profile_completion_percent == other.profile_completion_percent
            )
        return False

    def __hash__(self) -> int:
        """Make DashboardStats hashable."""
        return hash((
            self.upcoming_sessions_count,
            self.total_students,
            self.completed_sessions,
            self.total_earnings,
            self.profile_completion_percent,
        ))
