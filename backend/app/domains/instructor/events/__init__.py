"""Instructor domain events."""

from .instructor_onboarding_started import InstructorOnboardingStarted
from .instructor_onboarding_completed import InstructorOnboardingCompleted
from .instructor_submitted_for_review import InstructorSubmittedForReview
from .instructor_verified import InstructorVerified
from .instructor_rejected import InstructorRejected
from .instructor_suspended import InstructorSuspended
from .pricing_updated import PricingUpdated
from .profile_photo_updated import ProfilePhotoUpdated
from .intro_video_updated import IntroVideoUpdated

__all__ = [
    "InstructorOnboardingStarted",
    "InstructorOnboardingCompleted",
    "InstructorSubmittedForReview",
    "InstructorVerified",
    "InstructorRejected",
    "InstructorSuspended",
    "PricingUpdated",
    "ProfilePhotoUpdated",
    "IntroVideoUpdated",
]
