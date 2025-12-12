"""InstructorProfile domain entity with business logic."""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from ..value_objects import InstructorStatus, LanguageProficiency, Pricing, Rating
from ..events import (
    InstructorOnboardingStarted,
    InstructorOnboardingCompleted,
    InstructorSubmittedForReview,
    InstructorVerified,
    InstructorRejected,
    InstructorSuspended,
    PricingUpdated,
    ProfilePhotoUpdated,
    IntroVideoUpdated,
)


@dataclass
class InstructorProfile:
    """
    InstructorProfile aggregate root.

    Rich domain entity managing instructor lifecycle and business logic.
    """

    # Identity
    id: Optional[int] = None
    user_id: int = None

    # Value Objects
    status: InstructorStatus = field(default=InstructorStatus.DRAFT)
    languages_spoken: Optional[LanguageProficiency] = None
    pricing: Optional[Pricing] = None
    rating: Rating = field(default_factory=Rating.create_empty)

    # Profile Information
    country_of_birth: Optional[str] = None
    profile_photo_url: Optional[str] = None
    bio: Optional[str] = None
    teaching_experience: Optional[str] = None
    headline: Optional[str] = None
    intro_video_url: Optional[str] = None
    intro_video_thumbnail_url: Optional[str] = None

    # Onboarding Progress
    onboarding_step: int = 1
    is_onboarding_complete: bool = False

    # Statistics
    total_sessions_completed: int = 0
    total_earnings: float = 0.0

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Domain Events
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create_for_user(cls, user_id: int) -> "InstructorProfile":
        """
        Create instructor profile for a user.

        Args:
            user_id: User ID

        Returns:
            New InstructorProfile
        """
        profile = cls(
            user_id=user_id,
            status=InstructorStatus.DRAFT,
            onboarding_step=1,
            is_onboarding_complete=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Emit domain event
        profile._add_domain_event(
            InstructorOnboardingStarted(
                user_id=user_id,
                instructor_id=None,
                started_at=profile.created_at,
            )
        )

        return profile

    # ========================================================================
    # Onboarding Business Logic
    # ========================================================================

    def update_about(
        self,
        country_of_birth: str,
        languages_spoken: LanguageProficiency
    ) -> None:
        """
        Update instructor about information (Step 1).

        Args:
            country_of_birth: Country of birth
            languages_spoken: Languages spoken with proficiency
        """
        if not country_of_birth or not country_of_birth.strip():
            raise ValueError("Country of birth is required")

        self.country_of_birth = country_of_birth.strip()
        self.languages_spoken = languages_spoken
        self.updated_at = datetime.utcnow()

        # Progress to next step if not already advanced
        if self.onboarding_step == 1:
            self.onboarding_step = 2

    def update_profile_photo(self, photo_url: str) -> None:
        """
        Update profile photo (Step 2).

        Args:
            photo_url: Profile photo URL
        """
        if not photo_url or not photo_url.strip():
            raise ValueError("Profile photo URL is required")

        self.profile_photo_url = photo_url.strip()
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            ProfilePhotoUpdated(
                instructor_id=self.id,
                user_id=self.user_id,
                photo_url=photo_url,
                updated_at=self.updated_at,
            )
        )

        # Progress to next step
        if self.onboarding_step == 2:
            self.onboarding_step = 3

    def update_description(
        self,
        bio: str,
        teaching_experience: str,
        headline: str
    ) -> None:
        """
        Update description (Step 3).

        Args:
            bio: Biography - instructor's background and qualifications
            teaching_experience: Teaching style/methodology - how the instructor teaches
            headline: Profile headline - short tagline for the profile

        Business Rule: All three fields are required for a complete instructor profile.
        Students need this information to make informed booking decisions.
        """
        if not bio or not bio.strip():
            raise ValueError("Bio is required")
        if not teaching_experience or not teaching_experience.strip():
            raise ValueError("Teaching style is required")
        if not headline or not headline.strip():
            raise ValueError("Headline is required")

        self.bio = bio.strip()
        self.teaching_experience = teaching_experience.strip()
        self.headline = headline.strip()
        self.updated_at = datetime.utcnow()

        # Progress to next step
        if self.onboarding_step == 3:
            self.onboarding_step = 4

    def update_intro_video(
        self,
        video_url: str,
        thumbnail_url: Optional[str] = None
    ) -> None:
        """
        Update intro video (Step 4).

        Args:
            video_url: Intro video URL
            thumbnail_url: Optional video thumbnail URL
        """
        if not video_url or not video_url.strip():
            raise ValueError("Video URL is required")

        self.intro_video_url = video_url.strip()
        if thumbnail_url:
            self.intro_video_thumbnail_url = thumbnail_url.strip()
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            IntroVideoUpdated(
                instructor_id=self.id,
                user_id=self.user_id,
                video_url=video_url,
                updated_at=self.updated_at,
            )
        )

        # Progress to next step
        if self.onboarding_step == 4:
            self.onboarding_step = 5

    def update_pricing(self, pricing: Pricing) -> None:
        """
        Update pricing (Step 6).

        Args:
            pricing: Pricing value object
        """
        old_pricing = self.pricing
        self.pricing = pricing
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            PricingUpdated(
                instructor_id=self.id,
                user_id=self.user_id,
                old_regular_price=old_pricing.regular_price_float if old_pricing else None,
                new_regular_price=pricing.regular_price_float,
                updated_at=self.updated_at,
            )
        )

        # Progress to next step
        if self.onboarding_step == 6:
            self.onboarding_step = 7

    def complete_onboarding(self) -> None:
        """
        Complete instructor onboarding.

        Marks onboarding as complete. Full validation happens at submit_for_review().
        This allows instructors to complete the onboarding flow even if some optional
        fields are missing - they can fill them in later before submitting for review.
        """
        # Mark onboarding as complete
        self.is_onboarding_complete = True
        self.onboarding_step = 7
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            InstructorOnboardingCompleted(
                instructor_id=self.id,
                user_id=self.user_id,
                completed_at=self.updated_at,
            )
        )

    def validate_profile_completeness(self) -> list[str]:
        """
        Validate all required fields are completed.

        Returns:
            List of missing field error messages. Empty if all required fields are present.
        """
        missing = []
        if not self.country_of_birth:
            missing.append("Country of birth is required")
        if not self.languages_spoken:
            missing.append("Languages spoken are required")
        if not self.profile_photo_url:
            missing.append("Profile photo is required")
        if not self.bio:
            missing.append("Bio is required")
        if not self.teaching_experience:
            missing.append("Teaching style is required")
        if not self.headline:
            missing.append("Headline is required")
        if not self.intro_video_url:
            missing.append("Intro video is required")
        if not self.pricing:
            missing.append("Pricing is required")
        return missing

    def submit_for_review(self) -> None:
        """
        Submit profile for admin review.

        Can only submit if onboarding is complete and all required fields are filled.
        """
        if not self.is_onboarding_complete:
            raise ValueError("Cannot submit incomplete profile for review")

        # Validate all required fields before submitting
        missing_fields = self.validate_profile_completeness()
        if missing_fields:
            raise ValueError(f"Profile incomplete: {', '.join(missing_fields)}")

        if not self.status.can_submit_for_review():
            raise ValueError(f"Cannot submit profile with status: {self.status}")

        self.status = InstructorStatus.PENDING_REVIEW
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            InstructorSubmittedForReview(
                instructor_id=self.id,
                user_id=self.user_id,
                submitted_at=self.updated_at,
            )
        )

    # ========================================================================
    # Admin Actions
    # ========================================================================

    def verify(self, verified_by_admin_id: int) -> None:
        """
        Verify instructor profile (admin action).

        Args:
            verified_by_admin_id: ID of admin who verified
        """
        if not self.status.can_be_verified():
            raise ValueError(f"Cannot verify profile with status: {self.status}")

        self.status = InstructorStatus.VERIFIED
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            InstructorVerified(
                instructor_id=self.id,
                user_id=self.user_id,
                verified_by=verified_by_admin_id,
                verified_at=self.updated_at,
            )
        )

    def reject(self, reason: str, rejected_by_admin_id: int) -> None:
        """
        Reject instructor profile (admin action).

        Args:
            reason: Rejection reason
            rejected_by_admin_id: ID of admin who rejected
        """
        if self.status != InstructorStatus.PENDING_REVIEW:
            raise ValueError("Can only reject profiles pending review")

        self.status = InstructorStatus.REJECTED
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            InstructorRejected(
                instructor_id=self.id,
                user_id=self.user_id,
                reason=reason,
                rejected_by=rejected_by_admin_id,
                rejected_at=self.updated_at,
            )
        )

    def suspend(self, reason: str, suspended_by_admin_id: int) -> None:
        """
        Suspend instructor (admin action).

        Args:
            reason: Suspension reason
            suspended_by_admin_id: ID of admin who suspended
        """
        if not self.status.can_be_suspended():
            raise ValueError(f"Cannot suspend profile with status: {self.status}")

        self.status = InstructorStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            InstructorSuspended(
                instructor_id=self.id,
                user_id=self.user_id,
                reason=reason,
                suspended_by=suspended_by_admin_id,
                suspended_at=self.updated_at,
            )
        )

    # ========================================================================
    # Session & Earnings Management
    # ========================================================================

    def record_session_completion(self, earnings: float) -> None:
        """
        Record a completed session.

        Args:
            earnings: Amount earned from session
        """
        if earnings < 0:
            raise ValueError("Earnings cannot be negative")

        self.total_sessions_completed += 1
        self.total_earnings += earnings
        self.updated_at = datetime.utcnow()

    def add_review(self, score: float) -> None:
        """
        Add a new review and update rating.

        Args:
            score: Review score (1-5)
        """
        self.rating = self.rating.add_review(score)
        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Domain Properties
    # ========================================================================

    @property
    def is_verified(self) -> bool:
        """Check if instructor is verified."""
        return self.status.is_verified

    @property
    def can_accept_bookings(self) -> bool:
        """Check if can accept bookings."""
        return self.status.can_accept_bookings()

    @property
    def has_reviews(self) -> bool:
        """Check if has reviews."""
        return self.rating.has_reviews

    @property
    def is_highly_rated(self) -> bool:
        """Check if highly rated."""
        return self.rating.is_highly_rated

    # ========================================================================
    # Domain Events
    # ========================================================================

    def _add_domain_event(self, event) -> None:
        """Add domain event."""
        self._domain_events.append(event)

    def get_domain_events(self) -> List:
        """Get all domain events."""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear domain events."""
        self._domain_events.clear()

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, InstructorProfile):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.id) if self.id else hash(id(self))
