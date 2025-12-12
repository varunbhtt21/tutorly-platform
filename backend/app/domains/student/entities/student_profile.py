"""StudentProfile domain entity with business logic."""

from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass, field


@dataclass
class StudentProfile:
    """
    StudentProfile domain entity.

    Manages student profile information, learning preferences, and session history.
    """

    # Identity
    id: Optional[int] = None
    user_id: int = None

    # Profile Information
    profile_photo_url: Optional[str] = None
    learning_goals: Optional[str] = None
    preferred_language: Optional[str] = None

    # Preferences
    notification_preferences: Optional[Dict] = None
    preferred_session_duration: int = 50  # minutes

    # Statistics
    total_sessions_completed: int = 0
    total_spent: float = 0.0

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create_for_user(cls, user_id: int) -> "StudentProfile":
        """
        Create student profile for a user.

        Args:
            user_id: User ID

        Returns:
            New StudentProfile
        """
        profile = cls(
            user_id=user_id,
            notification_preferences={
                "email_notifications": True,
                "session_reminders": True,
                "booking_updates": True,
            },
            preferred_session_duration=50,
            total_sessions_completed=0,
            total_spent=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return profile

    # ========================================================================
    # Profile Management
    # ========================================================================

    def update_profile(
        self,
        profile_photo_url: Optional[str] = None,
        learning_goals: Optional[str] = None,
        preferred_language: Optional[str] = None,
        preferred_session_duration: Optional[int] = None,
        notification_preferences: Optional[Dict] = None,
    ) -> None:
        """
        Update student profile information.

        Args:
            profile_photo_url: URL to profile photo
            learning_goals: Learning goals and objectives
            preferred_language: Preferred language for tutoring
            preferred_session_duration: Preferred session duration in minutes
            notification_preferences: Notification preference settings
        """
        if profile_photo_url is not None:
            self.profile_photo_url = profile_photo_url.strip() if profile_photo_url else None

        if learning_goals is not None:
            self.learning_goals = learning_goals.strip() if learning_goals else None

        if preferred_language is not None:
            self.preferred_language = preferred_language.strip() if preferred_language else None

        if preferred_session_duration is not None:
            if preferred_session_duration <= 0:
                raise ValueError("Session duration must be greater than 0")
            self.preferred_session_duration = preferred_session_duration

        if notification_preferences is not None:
            self.notification_preferences = notification_preferences

        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Session & Spending Management
    # ========================================================================

    def record_session_completion(self, amount: float) -> None:
        """
        Record a completed session and amount spent.

        Args:
            amount: Amount spent for this session

        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        self.total_sessions_completed += 1
        self.total_spent += amount
        self.updated_at = datetime.utcnow()

    def increment_sessions(self) -> None:
        """Increment the total sessions completed count."""
        self.total_sessions_completed += 1
        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Domain Properties
    # ========================================================================

    @property
    def is_complete(self) -> bool:
        """Check if student profile is complete."""
        return (
            self.profile_photo_url is not None
            and self.learning_goals is not None
            and self.preferred_language is not None
        )

    @property
    def has_completed_sessions(self) -> bool:
        """Check if student has completed any sessions."""
        return self.total_sessions_completed > 0

    @property
    def average_session_cost(self) -> float:
        """Get average cost per session."""
        if self.total_sessions_completed == 0:
            return 0.0
        return round(self.total_spent / self.total_sessions_completed, 2)

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, StudentProfile):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.id) if self.id else hash(id(self))
