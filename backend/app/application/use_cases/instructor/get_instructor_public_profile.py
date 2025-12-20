"""
Use case for getting instructor public profile with user information.

This use case aggregates instructor profile data with user information
(first_name, last_name) for public profile display. It follows Clean
Architecture by orchestrating data retrieval through repositories.

Key Responsibilities:
1. Fetch instructor profile by ID
2. Retrieve associated user information
3. Validate profile visibility (only verified profiles for public)
4. Return aggregated data transfer object

Usage:
    use_case = GetInstructorPublicProfileUseCase(instructor_repo)
    result = use_case.execute(instructor_id=11, requesting_user_id=None)
"""

from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.instructor.value_objects import InstructorStatus
from app.domains.user.entities import User


@dataclass
class LanguageDTO:
    """Language data transfer object."""
    language: str
    proficiency: str


@dataclass
class InstructorPublicProfileDTO:
    """
    Data transfer object for instructor public profile.

    Contains instructor profile data along with user information
    for public display purposes.
    """
    id: int
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    status: InstructorStatus
    country_of_birth: Optional[str]
    languages: List[LanguageDTO]
    profile_photo_url: Optional[str]
    bio: Optional[str]
    teaching_experience: Optional[str]
    headline: Optional[str]
    intro_video_url: Optional[str]
    hourly_rate: Optional[Decimal]
    trial_lesson_price: Optional[Decimal]
    onboarding_step: int
    is_onboarding_complete: bool

    @classmethod
    def from_profile_and_user(
        cls,
        profile: InstructorProfile,
        user: Optional[User],
    ) -> "InstructorPublicProfileDTO":
        """
        Create DTO from domain entities.

        Args:
            profile: Instructor profile entity
            user: User entity (optional, for name info)

        Returns:
            InstructorPublicProfileDTO instance
        """
        # Parse languages
        languages = []
        if profile.languages_spoken:
            for lang in profile.languages_spoken.languages:
                languages.append(LanguageDTO(
                    language=lang.name,
                    proficiency=lang.proficiency.value
                ))

        # Parse pricing
        hourly_rate = None
        trial_price = None
        if profile.pricing:
            hourly_rate = Decimal(str(profile.pricing.regular_session_price))
            if profile.pricing.trial_session_price:
                trial_price = Decimal(str(profile.pricing.trial_session_price))

        return cls(
            id=profile.id,
            user_id=profile.user_id,
            first_name=user.first_name if user else None,
            last_name=user.last_name if user else None,
            status=profile.status,
            country_of_birth=profile.country_of_birth,
            languages=languages,
            profile_photo_url=profile.profile_photo_url,
            bio=profile.bio,
            teaching_experience=profile.teaching_experience,
            headline=profile.headline,
            intro_video_url=profile.intro_video_url,
            hourly_rate=hourly_rate,
            trial_lesson_price=trial_price,
            onboarding_step=profile.onboarding_step,
            is_onboarding_complete=profile.is_onboarding_complete,
        )


class GetInstructorPublicProfileUseCase:
    """
    Use case for retrieving instructor public profile with user information.

    This use case handles the aggregation of instructor profile data
    with user information (name) for public profile display. It ensures
    proper visibility rules (only verified profiles for unauthenticated users).
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize the use case.

        Args:
            instructor_repo: Repository for instructor profile data
        """
        self.instructor_repo = instructor_repo

    def execute(
        self,
        instructor_id: int,
        requesting_user_id: Optional[int] = None,
    ) -> InstructorPublicProfileDTO:
        """
        Execute the use case to get instructor public profile.

        Args:
            instructor_id: The instructor profile ID to fetch
            requesting_user_id: Optional ID of the requesting user
                               (for visibility checks)

        Returns:
            InstructorPublicProfileDTO with aggregated data

        Raises:
            ValueError: If profile not found
            PermissionError: If profile is not public and user is unauthorized
        """
        # Fetch profile with user data
        result = self.instructor_repo.get_with_user(instructor_id)

        if not result:
            raise ValueError(f"Instructor profile {instructor_id} not found")

        profile, user = result

        # Visibility check: only verified profiles for unauthenticated users
        if not requesting_user_id and profile.status != InstructorStatus.VERIFIED:
            raise PermissionError("Instructor profile is not publicly visible")

        return InstructorPublicProfileDTO.from_profile_and_user(profile, user)
