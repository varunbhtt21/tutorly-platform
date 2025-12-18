"""
Instructor Router - Pure DDD Implementation.

HTTP endpoints for instructor onboarding and profile management using Pure DDD principles:
- Thin controllers: Only handle HTTP concerns
- Delegate business logic to use cases
- Use domain entities and value objects
- Proper error handling and HTTP status codes
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.domains.user.entities import User
from app.domains.instructor.entities import InstructorProfile, Education, Experience
from app.domains.instructor.value_objects import InstructorStatus
from app.core.dependencies import (
    get_current_instructor,
    get_current_instructor_allow_inactive,
    get_current_admin,
    get_current_user,
    get_optional_current_user,
    get_create_instructor_profile_use_case,
    get_update_instructor_about_use_case,
    get_update_instructor_pricing_use_case,
    get_complete_onboarding_use_case,
    get_submit_for_review_use_case,
    get_verify_instructor_use_case,
    get_add_education_use_case,
    get_add_experience_use_case,
    get_instructor_repository,
    get_instructor_dashboard_use_case,
    get_user_repository,
)
from app.domains.user.repositories import IUserRepository
from app.application.use_cases.instructor import (
    CreateInstructorProfileUseCase,
    UpdateInstructorAboutUseCase,
    UpdateInstructorPricingUseCase,
    CompleteInstructorOnboardingUseCase,
    SubmitForReviewUseCase,
    VerifyInstructorUseCase,
    AddEducationUseCase,
    AddExperienceUseCase,
    GetInstructorDashboardUseCase,
)
from app.domains.instructor.entities import InstructorDashboard
from app.domains.instructor.value_objects import DashboardStats
from app.domains.instructor.repositories import IInstructorProfileRepository


# ============================================================================
# Request/Response DTOs (Inline Pydantic Models)
# ============================================================================


class LanguageInput(BaseModel):
    """Language proficiency input."""
    language: str = Field(..., min_length=1, max_length=50)
    proficiency: str = Field(..., description="Native, fluent, intermediate, or basic")


class SubjectInput(BaseModel):
    """Subject selection input."""
    subject_id: int
    proficiency_level: str = Field(..., description="Expert, advanced, or intermediate")


class EducationInput(BaseModel):
    """Education credential input."""
    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_year: int = Field(..., ge=1950, le=2100)
    end_year: Optional[int] = Field(None, ge=1950, le=2100)
    description: Optional[str] = None


class ExperienceInput(BaseModel):
    """Work experience input."""
    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=100)
    start_year: int = Field(..., ge=1950, le=2100)
    end_year: Optional[int] = Field(None, ge=1950, le=2100)
    description: Optional[str] = None
    is_current: bool = False


# Step 1: About Information
class OnboardingStep1Request(BaseModel):
    """Step 1: Basic about information."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    country: str = Field(..., min_length=1, max_length=100)
    languages: List[LanguageInput] = Field(..., min_items=1)
    phone_number: Optional[str] = None


class OnboardingStep1Response(BaseModel):
    """Step 1 completion response."""
    profile_id: int
    onboarding_step: int


# Step 2: Photo Upload
class OnboardingStep2Request(BaseModel):
    """Step 2: Profile photo."""
    photo_url: str = Field(..., description="URL to uploaded photo")


class OnboardingStep2Response(BaseModel):
    """Step 2 completion response."""
    profile_id: int
    onboarding_step: int
    photo_url: str


# Step 3: Description
class OnboardingStep3Request(BaseModel):
    """Step 3: Bio and teaching information."""
    bio: str = Field(..., min_length=50, max_length=2000)
    headline: str = Field(..., min_length=10, max_length=200)
    years_of_experience: int = Field(..., ge=0, le=100)
    teaching_style: Optional[str] = Field(None, max_length=1000)


class OnboardingStep3Response(BaseModel):
    """Step 3 completion response."""
    profile_id: int
    onboarding_step: int


# Step 4: Video Upload
class OnboardingStep4Request(BaseModel):
    """Step 4: Introduction video."""
    video_url: str = Field(..., description="URL to uploaded video")


class OnboardingStep4Response(BaseModel):
    """Step 4 completion response."""
    profile_id: int
    onboarding_step: int
    video_url: str


# Step 5: Subject Selection
class OnboardingStep5Request(BaseModel):
    """Step 5: Subject selection."""
    subjects: List[SubjectInput] = Field(..., min_items=1)


class OnboardingStep5Response(BaseModel):
    """Step 5 completion response."""
    profile_id: int
    onboarding_step: int
    subjects_count: int


# Step 6: Pricing
class OnboardingStep6Request(BaseModel):
    """Step 6: Pricing configuration."""
    hourly_rate: Decimal = Field(..., ge=Decimal("5.00"), le=Decimal("200.00"))
    trial_lesson_price: Optional[Decimal] = Field(None, ge=Decimal("1.00"), le=Decimal("100.00"))


class OnboardingStep6Response(BaseModel):
    """Step 6 completion response."""
    profile_id: int
    onboarding_step: int
    hourly_rate: Decimal
    trial_lesson_price: Optional[Decimal]


# Step 7: Background (Education & Experience)
class OnboardingStep7Request(BaseModel):
    """Step 7: Education and work experience."""
    education: List[EducationInput] = Field(default_factory=list)
    experience: List[ExperienceInput] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class OnboardingStep7Response(BaseModel):
    """Step 7 completion response (final step)."""
    profile_id: int
    onboarding_step: int
    profile_status: InstructorStatus


# Profile Response
class LanguageResponse(BaseModel):
    """Language proficiency response."""
    language: str
    proficiency: str


class SubjectResponse(BaseModel):
    """Subject response."""
    id: int
    name: str
    proficiency_level: str


class EducationResponse(BaseModel):
    """Education response."""
    id: int
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: Optional[int]
    description: Optional[str]

    @classmethod
    def from_domain(cls, education: Education) -> "EducationResponse":
        """Create response from domain entity."""
        return cls(
            id=education.id,
            institution=education.institution_name,
            degree=education.degree,
            field_of_study=education.field_of_study,
            start_year=education.year_of_graduation,  # Using graduation year as end year
            end_year=education.year_of_graduation,
            description=None,  # Not available in domain entity
        )


class ExperienceResponse(BaseModel):
    """Experience response."""
    id: int
    company: str
    position: str
    start_year: int
    end_year: Optional[int]
    description: Optional[str]
    is_current: bool

    @classmethod
    def from_domain(cls, experience: Experience) -> "ExperienceResponse":
        """Create response from domain entity."""
        # Extract year from YYYY-MM date strings
        start_year = int(experience.start_date.split('-')[0]) if experience.start_date else None
        end_year = int(experience.end_date.split('-')[0]) if experience.end_date and experience.end_date != "Present" else None

        return cls(
            id=experience.id,
            company=experience.company_name,
            position=experience.position,
            start_year=start_year,
            end_year=end_year,
            description=experience.description,
            is_current=experience.is_current,
        )


class InstructorProfileResponse(BaseModel):
    """Complete instructor profile response."""
    id: int
    user_id: int
    status: InstructorStatus
    country_of_birth: Optional[str]
    languages: List[LanguageResponse]
    profile_photo_url: Optional[str]
    bio: Optional[str]
    teaching_experience: Optional[str]
    headline: Optional[str]
    intro_video_url: Optional[str]
    hourly_rate: Optional[Decimal]
    trial_lesson_price: Optional[Decimal]
    onboarding_step: int
    is_onboarding_complete: bool
    education: List[EducationResponse]
    experience: List[ExperienceResponse]

    @classmethod
    def from_domain(cls, profile: InstructorProfile, education: List[Education] = None, experience: List[Experience] = None) -> "InstructorProfileResponse":
        """Create response from domain entity."""
        # Parse languages
        languages = []
        if profile.languages_spoken:
            for lang in profile.languages_spoken.languages:
                languages.append(LanguageResponse(
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

        # Convert education and experience
        edu_list = [EducationResponse.from_domain(e) for e in (education or [])]
        exp_list = [ExperienceResponse.from_domain(e) for e in (experience or [])]

        return cls(
            id=profile.id,
            user_id=profile.user_id,
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
            education=edu_list,
            experience=exp_list,
        )


# Admin Verification
class VerifyInstructorRequest(BaseModel):
    """Admin verification request."""
    action: str = Field(..., pattern="^(approve|reject)$")
    rejection_reason: Optional[str] = None


class VerifyInstructorResponse(BaseModel):
    """Verification response."""
    profile_id: int
    profile_status: InstructorStatus
    message: str


# Search - Language item matching frontend LanguageResponse
class LanguageListItem(BaseModel):
    """Language item for search results."""
    language: str
    proficiency: str = "Native"


# Search - InstructorListItem matches frontend InstructorProfile type
class InstructorListItem(BaseModel):
    """Instructor list item for search results - matches frontend InstructorProfile."""
    id: int
    user_id: int
    status: InstructorStatus = InstructorStatus.VERIFIED
    country_of_birth: Optional[str] = None
    languages: List[LanguageListItem] = []
    profile_photo_url: Optional[str] = None
    bio: Optional[str] = None
    teaching_experience: Optional[str] = None
    headline: Optional[str] = None
    intro_video_url: Optional[str] = None
    hourly_rate: Optional[Decimal] = None
    trial_lesson_price: Optional[Decimal] = None
    onboarding_step: int = 7
    is_onboarding_complete: bool = True
    education: List[EducationResponse] = []
    experience: List[ExperienceResponse] = []


class InstructorSearchResponse(BaseModel):
    """Search results response."""
    total: int
    skip: int
    limit: int
    instructors: List[InstructorListItem]


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Dashboard DTOs
class DashboardStatsResponse(BaseModel):
    """Dashboard statistics DTO."""
    upcoming_sessions_count: int
    total_students: int
    completed_sessions: int
    total_earnings: float
    profile_completion_percent: int

    @classmethod
    def from_domain(cls, stats: DashboardStats) -> "DashboardStatsResponse":
        """Create response from domain value object."""
        return cls(
            upcoming_sessions_count=stats.upcoming_sessions_count,
            total_students=stats.total_students,
            completed_sessions=stats.completed_sessions,
            total_earnings=stats.earnings_float,
            profile_completion_percent=stats.profile_completion_percent,
        )


class UserBasicInfoResponse(BaseModel):
    """Basic user info for dashboard."""
    id: int
    first_name: str
    last_name: str
    email: str

    @classmethod
    def from_domain(cls, user) -> "UserBasicInfoResponse":
        """Create response from domain entity."""
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=str(user.email),
        )


class UpcomingSessionResponse(BaseModel):
    """Upcoming session DTO for instructor dashboard."""
    id: int
    student_id: int
    student_name: str
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    session_type: str
    status: str
    is_trial: bool
    amount: Decimal
    currency: str


class InstructorDashboardResponse(BaseModel):
    """Complete dashboard response DTO."""
    profile: InstructorProfileResponse
    user: UserBasicInfoResponse
    stats: DashboardStatsResponse
    upcoming_sessions: List[UpcomingSessionResponse]


# Create router
router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def handle_domain_exception(e: Exception) -> None:
    """
    Convert domain exceptions to HTTP exceptions.

    Args:
        e: Exception from domain or use case layer

    Raises:
        HTTPException: Appropriate HTTP exception
    """
    error_message = str(e)

    if "not found" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": error_message},
        )
    elif "already exists" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "ALREADY_EXISTS", "message": error_message},
        )
    elif "invalid" in error_message.lower() or "validation" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "VALIDATION_ERROR", "message": error_message},
        )
    elif "permission" in error_message.lower() or "forbidden" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "FORBIDDEN", "message": error_message},
        )
    elif "required" in error_message.lower():
        # Handle domain validation errors about required fields
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INCOMPLETE_PROFILE", "message": error_message},
        )
    else:
        # Log unexpected errors for debugging
        import traceback
        print(f"Unexpected error: {error_message}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": error_message},
        )


# ============================================================================
# Onboarding Endpoints (Instructor Only)
# ============================================================================


@router.post(
    "/onboarding/step-1",
    response_model=OnboardingStep1Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 1: About Information",
    description="Complete the first step of instructor onboarding with basic information.",
)
async def onboarding_step_1(
    request: OnboardingStep1Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    create_profile_use_case: CreateInstructorProfileUseCase = Depends(get_create_instructor_profile_use_case),
    update_about_use_case: UpdateInstructorAboutUseCase = Depends(get_update_instructor_about_use_case),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep1Response:
    """Complete step 1: Basic information about the instructor."""
    try:
        # Get or create instructor profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            profile = create_profile_use_case.execute(user_id=current_user.id)

        # Convert languages to dict format
        languages_data = [
            {"language": lang.language, "proficiency": lang.proficiency}
            for lang in request.languages
        ]

        # Update about information
        updated_profile = update_about_use_case.execute(
            instructor_id=profile.id,
            country_of_birth=request.country,
            languages=languages_data,
        )

        return OnboardingStep1Response(
            profile_id=updated_profile.id,
            onboarding_step=updated_profile.onboarding_step,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/onboarding/step-2",
    response_model=OnboardingStep2Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 2: Photo Upload",
    description="Upload and set profile photo for instructor.",
)
async def onboarding_step_2(
    request: OnboardingStep2Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep2Response:
    """Complete step 2: Profile photo upload."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Update photo using domain logic
        profile.update_profile_photo(request.photo_url)

        # Save updated profile
        updated_profile = instructor_repo.update(profile)

        return OnboardingStep2Response(
            profile_id=updated_profile.id,
            onboarding_step=updated_profile.onboarding_step,
            photo_url=updated_profile.profile_photo_url or "",
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/onboarding/step-3",
    response_model=OnboardingStep3Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 3: Description",
    description="Add bio, headline, and teaching experience details.",
)
async def onboarding_step_3(
    request: OnboardingStep3Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep3Response:
    """Complete step 3: Bio and teaching experience."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Update description using domain logic
        profile.update_description(
            bio=request.bio,
            headline=request.headline,
            teaching_experience=request.teaching_style,
        )

        # Save updated profile
        updated_profile = instructor_repo.update(profile)

        return OnboardingStep3Response(
            profile_id=updated_profile.id,
            onboarding_step=updated_profile.onboarding_step,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/onboarding/step-4",
    response_model=OnboardingStep4Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 4: Video Upload",
    description="Upload and set introduction video for instructor profile.",
)
async def onboarding_step_4(
    request: OnboardingStep4Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep4Response:
    """Complete step 4: Introduction video upload."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Update video using domain logic
        profile.update_intro_video(request.video_url)

        # Save updated profile
        updated_profile = instructor_repo.update(profile)

        return OnboardingStep4Response(
            profile_id=updated_profile.id,
            onboarding_step=updated_profile.onboarding_step,
            video_url=updated_profile.intro_video_url or "",
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/onboarding/step-5",
    response_model=OnboardingStep5Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 5: Subject Selection",
    description="Select subjects to teach with proficiency levels.",
)
async def onboarding_step_5(
    request: OnboardingStep5Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep5Response:
    """Complete step 5: Subject selection with proficiency levels."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Note: Subject management would require additional use cases
        # For now, just advance the step
        if profile.onboarding_step == 5:
            profile.onboarding_step = 6
        profile.updated_at = datetime.utcnow()

        # Save updated profile
        updated_profile = instructor_repo.update(profile)

        return OnboardingStep5Response(
            profile_id=updated_profile.id,
            onboarding_step=updated_profile.onboarding_step,
            subjects_count=len(request.subjects),
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/onboarding/step-6",
    response_model=OnboardingStep6Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 6: Pricing",
    description="Set hourly rate and trial lesson pricing.",
)
async def onboarding_step_6(
    request: OnboardingStep6Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    update_pricing_use_case: UpdateInstructorPricingUseCase = Depends(get_update_instructor_pricing_use_case),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep6Response:
    """Complete step 6: Pricing configuration."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Update pricing using use case
        updated_profile = update_pricing_use_case.execute(
            instructor_id=profile.id,
            regular_price=float(request.hourly_rate),
            trial_price=float(request.trial_lesson_price) if request.trial_lesson_price else None,
        )

        return OnboardingStep6Response(
            profile_id=updated_profile.id,
            onboarding_step=updated_profile.onboarding_step,
            hourly_rate=request.hourly_rate,
            trial_lesson_price=request.trial_lesson_price,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/onboarding/step-7",
    response_model=OnboardingStep7Response,
    status_code=status.HTTP_200_OK,
    summary="Complete Step 7: Background (Final Step)",
    description="Add education, experience, and certifications to complete onboarding.",
)
async def onboarding_step_7(
    request: OnboardingStep7Request,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    add_education_use_case: AddEducationUseCase = Depends(get_add_education_use_case),
    add_experience_use_case: AddExperienceUseCase = Depends(get_add_experience_use_case),
    complete_onboarding_use_case: CompleteInstructorOnboardingUseCase = Depends(get_complete_onboarding_use_case),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> OnboardingStep7Response:
    """Complete step 7: Education and work experience (final step)."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Add education entries
        for edu in request.education:
            add_education_use_case.execute(
                instructor_id=profile.id,
                institution_name=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                year_of_graduation=edu.end_year or edu.start_year,
                certificate_url=None,  # Not provided in this step
            )

        # Add experience entries
        for exp in request.experience:
            # Convert year integers to YYYY-MM date strings
            start_date = f"{exp.start_year}-01"  # Default to January
            end_date = None if exp.is_current else (f"{exp.end_year}-12" if exp.end_year else None)

            add_experience_use_case.execute(
                instructor_id=profile.id,
                company_name=exp.company,
                position=exp.position,
                start_date=start_date,
                end_date=end_date,
                description=exp.description,
                is_current=exp.is_current,
            )

        # Complete onboarding
        completed_profile = complete_onboarding_use_case.execute(instructor_id=profile.id)

        return OnboardingStep7Response(
            profile_id=completed_profile.id,
            onboarding_step=completed_profile.onboarding_step,
            profile_status=completed_profile.status,
        )

    except ValueError as e:
        import traceback
        print(f"Step 7 ValueError: {e}")
        traceback.print_exc()
        handle_domain_exception(e)
    except Exception as e:
        import traceback
        print(f"Step 7 Exception: {e}")
        traceback.print_exc()
        handle_domain_exception(e)


# ============================================================================
# Profile Management Endpoints
# ============================================================================


@router.get(
    "/profile/me",
    response_model=InstructorProfileResponse,
    summary="Get My Instructor Profile",
    description="Get the current instructor's complete profile.",
)
async def get_my_profile(
    current_user: User = Depends(get_current_instructor_allow_inactive),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> InstructorProfileResponse:
    """Get the current instructor's profile with all related data."""
    try:
        # Get profile
        profile = instructor_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError(f"Instructor profile not found for user {current_user.id}")

        # Get related entities
        # Note: These would come from separate repositories in a full implementation
        education = []
        experience = []

        return InstructorProfileResponse.from_domain(profile, education, experience)

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "/profile/{instructor_id}",
    response_model=InstructorProfileResponse,
    summary="Get Instructor Profile by ID",
    description="Get a specific instructor's public profile (verified instructors only).",
)
async def get_instructor_profile(
    instructor_id: int,
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> InstructorProfileResponse:
    """
    Get instructor profile by ID.

    Public endpoint - only returns verified instructor profiles.
    Authenticated users can see more details.
    """
    try:
        # Get profile
        profile = instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile {instructor_id} not found")

        # Only show verified profiles to public
        if not current_user and profile.status != InstructorStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instructor profile not found",
            )

        # Get related entities
        education = []
        experience = []

        return InstructorProfileResponse.from_domain(profile, education, experience)

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# Dashboard Endpoints
# ============================================================================


@router.get(
    "/dashboard",
    response_model=InstructorDashboardResponse,
    summary="Get Instructor Dashboard",
    description="Get complete dashboard data including profile, stats, and upcoming sessions.",
)
async def get_instructor_dashboard(
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: GetInstructorDashboardUseCase = Depends(get_instructor_dashboard_use_case),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> InstructorDashboardResponse:
    """
    Get instructor dashboard data.

    Returns complete dashboard including:
    - Profile information (photo, bio, languages, pricing)
    - User information (name, email)
    - Statistics (sessions, students, earnings)
    - Upcoming sessions with student details

    Raises:
    - 404: Instructor profile not found
    """
    try:
        dashboard = use_case.execute(current_user.id)

        # Build student name cache for upcoming sessions
        student_ids = {s.student_id for s in dashboard.upcoming_sessions}
        student_cache = {}
        for student_id in student_ids:
            student = user_repo.get_by_id(student_id)
            if student:
                student_cache[student_id] = f"{student.first_name} {student.last_name}"
            else:
                student_cache[student_id] = "Unknown Student"

        # Build upcoming sessions response with student names
        upcoming_sessions = [
            UpcomingSessionResponse(
                id=session.id,
                student_id=session.student_id,
                student_name=student_cache.get(session.student_id, "Unknown Student"),
                start_at=session.start_at,
                end_at=session.end_at,
                duration_minutes=session.duration_minutes,
                session_type=session.session_type.value,
                status=session.status.value,
                is_trial=session.is_trial,
                amount=session.amount,
                currency=session.currency,
            )
            for session in dashboard.upcoming_sessions
        ]

        return InstructorDashboardResponse(
            profile=InstructorProfileResponse.from_domain(dashboard.profile),
            user=UserBasicInfoResponse.from_domain(dashboard.user),
            stats=DashboardStatsResponse.from_domain(dashboard.stats),
            upcoming_sessions=upcoming_sessions,
        )
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# Admin Verification Endpoints
# ============================================================================


@router.post(
    "/verify/{instructor_id}",
    response_model=VerifyInstructorResponse,
    summary="Verify or Reject Instructor (Admin Only)",
    description="Admin endpoint to approve or reject instructor profiles.",
)
async def verify_instructor(
    instructor_id: int,
    request: VerifyInstructorRequest,
    current_user: User = Depends(get_current_admin),
    verify_use_case: VerifyInstructorUseCase = Depends(get_verify_instructor_use_case),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> VerifyInstructorResponse:
    """Verify or reject an instructor profile (admin only)."""
    try:
        if request.action == "approve":
            # Approve instructor
            profile = verify_use_case.execute(
                instructor_id=instructor_id,
                verified_by_admin_id=current_user.id,
            )
            message = "Instructor profile approved successfully"
        else:
            # Reject instructor
            profile = instructor_repo.get_by_id(instructor_id)
            if not profile:
                raise ValueError(f"Instructor profile {instructor_id} not found")

            profile.reject(rejection_reason=request.rejection_reason)
            profile = instructor_repo.update(profile)
            message = "Instructor profile rejected"

        return VerifyInstructorResponse(
            profile_id=profile.id,
            profile_status=profile.status,
            message=message,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# Search Endpoints (Public)
# ============================================================================


@router.get(
    "/search",
    response_model=InstructorSearchResponse,
    summary="Search Instructors",
    description="Search for verified instructors with various filters.",
)
async def search_instructors(
    min_price: Optional[Decimal] = Query(None, ge=Decimal("0.00"), description="Minimum hourly rate"),
    max_price: Optional[Decimal] = Query(None, le=Decimal("1000.00"), description="Maximum hourly rate"),
    language: Optional[str] = Query(None, description="Filter by language"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> InstructorSearchResponse:
    """Search for verified instructors with filters."""
    try:
        # Get all verified instructors
        profiles = instructor_repo.get_all(
            status=InstructorStatus.VERIFIED,
            skip=0,  # We'll filter in memory for now, then paginate
            limit=1000,  # Get more to filter
        )

        # Apply filters
        filtered_profiles = []
        for profile in profiles:
            # Price filter
            if profile.pricing:
                hourly_rate = float(profile.pricing.regular_session_price)
                if min_price is not None and hourly_rate < float(min_price):
                    continue
                if max_price is not None and hourly_rate > float(max_price):
                    continue

            # Language filter
            if language and profile.languages_spoken:
                lang_names = [lang.name.lower() for lang in profile.languages_spoken.languages]
                if language.lower() not in lang_names:
                    continue

            filtered_profiles.append(profile)

        # Calculate total before pagination
        total = len(filtered_profiles)

        # Apply pagination
        paginated_profiles = filtered_profiles[skip:skip + limit]

        # Convert to response DTOs
        instructors = []
        for profile in paginated_profiles:
            # Extract languages as LanguageListItem objects
            languages_list = []
            if profile.languages_spoken:
                languages_list = [
                    LanguageListItem(
                        language=lang.name,
                        proficiency=lang.proficiency.value if hasattr(lang, 'proficiency') else "Native"
                    )
                    for lang in profile.languages_spoken.languages
                ]

            # Extract pricing
            hourly_rate = None
            trial_price = None
            if profile.pricing:
                hourly_rate = Decimal(str(profile.pricing.regular_session_price))
                if profile.pricing.trial_session_price:
                    trial_price = Decimal(str(profile.pricing.trial_session_price))

            instructors.append(InstructorListItem(
                id=profile.id,
                user_id=profile.user_id,
                status=profile.status,
                country_of_birth=profile.country_of_birth,
                languages=languages_list,
                profile_photo_url=profile.profile_photo_url,
                bio=profile.bio,
                teaching_experience=profile.teaching_experience,
                headline=profile.headline,
                intro_video_url=profile.intro_video_url,
                hourly_rate=hourly_rate,
                trial_lesson_price=trial_price,
                onboarding_step=profile.onboarding_step,
                is_onboarding_complete=profile.is_onboarding_complete,
                education=[],  # Can be populated if needed
                experience=[],  # Can be populated if needed
            ))

        return InstructorSearchResponse(
            total=total,
            skip=skip,
            limit=limit,
            instructors=instructors,
        )

    except Exception as e:
        handle_domain_exception(e)
