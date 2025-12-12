"""
Dependency Injection for Pure DDD Architecture.

Provides dependencies for:
- Repository implementations (Infrastructure layer)
- Use cases (Application layer)
- Authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import decode_token, get_password_hash, verify_password

# Domain repository interfaces
from app.domains.user.repositories import IUserRepository
from app.domains.instructor.repositories import (
    IInstructorProfileRepository,
    IEducationRepository,
    IExperienceRepository,
)
from app.domains.student.repositories import IStudentProfileRepository
from app.domains.file.repositories import IFileRepository
from app.domains.subject.repositories import ISubjectRepository, IInstructorSubjectRepository
from app.domains.scheduling.repositories import (
    IAvailabilityRepository,
    ISessionRepository,
    ITimeOffRepository,
    IBookingSlotRepository,
)

# Infrastructure repository implementations
from app.infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.repositories.instructor_repository_impl import SQLAlchemyInstructorProfileRepository
from app.infrastructure.repositories.student_repository_impl import SQLAlchemyStudentProfileRepository
from app.infrastructure.repositories.education_repository_impl import SQLAlchemyEducationRepository
from app.infrastructure.repositories.experience_repository_impl import SQLAlchemyExperienceRepository
from app.infrastructure.repositories.file_repository_impl import SQLAlchemyFileRepository
from app.infrastructure.repositories.subject_repository_impl import SQLAlchemySubjectRepository
from app.infrastructure.repositories.instructor_subject_repository_impl import SQLAlchemyInstructorSubjectRepository
from app.infrastructure.repositories.availability_repository_impl import AvailabilityRepositoryImpl
from app.infrastructure.repositories.session_repository_impl import SessionRepositoryImpl
from app.infrastructure.repositories.time_off_repository_impl import TimeOffRepositoryImpl
from app.infrastructure.repositories.booking_slot_repository_impl import BookingSlotRepositoryImpl

# Domain entities
from app.domains.user.entities import User
from app.domains.user.value_objects import UserRole, UserStatus

# Application layer use cases
from app.application.use_cases.user import (
    RegisterUserUseCase,
    VerifyEmailUseCase,
    LoginUserUseCase,
    UpdateUserProfileUseCase,
)
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
from app.application.use_cases.student import (
    CreateStudentProfileUseCase,
    UpdateStudentProfileUseCase,
    RecordSessionCompletionUseCase,
)
from app.application.use_cases.file import (
    UploadFileUseCase,
    DeleteFileUseCase,
    GetFileUseCase,
    ListUserFilesUseCase,
)
from app.application.use_cases.scheduling import (
    SetAvailabilityUseCase,
    GetCalendarViewUseCase,
    DeleteAvailabilityUseCase,
    UpdateAvailabilityUseCase,
    AddTimeOffUseCase,
    DeleteTimeOffUseCase,
    UpdateSlotUseCase,
    DeleteSlotUseCase,
)


# HTTP Bearer token security scheme
security = HTTPBearer()


# ============================================================================
# Repository Dependencies (Infrastructure Layer)
# ============================================================================


def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    """Get User repository implementation."""
    return SQLAlchemyUserRepository(db)


def get_instructor_repository(db: Session = Depends(get_db)) -> IInstructorProfileRepository:
    """Get InstructorProfile repository implementation."""
    return SQLAlchemyInstructorProfileRepository(db)


def get_student_repository(db: Session = Depends(get_db)) -> IStudentProfileRepository:
    """Get StudentProfile repository implementation."""
    return SQLAlchemyStudentProfileRepository(db)


def get_education_repository(db: Session = Depends(get_db)) -> IEducationRepository:
    """Get Education repository implementation."""
    return SQLAlchemyEducationRepository(db)


def get_experience_repository(db: Session = Depends(get_db)) -> IExperienceRepository:
    """Get Experience repository implementation."""
    return SQLAlchemyExperienceRepository(db)


def get_file_repository(db: Session = Depends(get_db)) -> IFileRepository:
    """Get File repository implementation."""
    return SQLAlchemyFileRepository(db)


def get_subject_repository(db: Session = Depends(get_db)) -> ISubjectRepository:
    """Get Subject repository implementation."""
    return SQLAlchemySubjectRepository(db)


def get_instructor_subject_repository(db: Session = Depends(get_db)) -> IInstructorSubjectRepository:
    """Get InstructorSubject repository implementation."""
    return SQLAlchemyInstructorSubjectRepository(db)


# ============================================================================
# Use Case Dependencies (Application Layer)
# ============================================================================

# User Use Cases

def get_register_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> RegisterUserUseCase:
    """Get RegisterUser use case."""
    return RegisterUserUseCase(user_repo)


def get_verify_email_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> VerifyEmailUseCase:
    """Get VerifyEmail use case."""
    return VerifyEmailUseCase(user_repo)


def get_login_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> LoginUserUseCase:
    """Get LoginUser use case."""
    return LoginUserUseCase(user_repo)


def get_update_user_profile_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> UpdateUserProfileUseCase:
    """Get UpdateUserProfile use case."""
    return UpdateUserProfileUseCase(user_repo)


# Instructor Use Cases

def get_create_instructor_profile_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> CreateInstructorProfileUseCase:
    """Get CreateInstructorProfile use case."""
    return CreateInstructorProfileUseCase(instructor_repo)


def get_update_instructor_about_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> UpdateInstructorAboutUseCase:
    """Get UpdateInstructorAbout use case."""
    return UpdateInstructorAboutUseCase(instructor_repo)


def get_update_instructor_pricing_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> UpdateInstructorPricingUseCase:
    """Get UpdateInstructorPricing use case."""
    return UpdateInstructorPricingUseCase(instructor_repo)


def get_complete_onboarding_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> CompleteInstructorOnboardingUseCase:
    """Get CompleteInstructorOnboarding use case."""
    return CompleteInstructorOnboardingUseCase(instructor_repo)


def get_submit_for_review_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> SubmitForReviewUseCase:
    """Get SubmitForReview use case."""
    return SubmitForReviewUseCase(instructor_repo)


def get_verify_instructor_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> VerifyInstructorUseCase:
    """Get VerifyInstructor use case."""
    return VerifyInstructorUseCase(instructor_repo)


def get_add_education_use_case(
    education_repo: IEducationRepository = Depends(get_education_repository),
) -> AddEducationUseCase:
    """Get AddEducation use case."""
    return AddEducationUseCase(education_repo)


def get_add_experience_use_case(
    experience_repo: IExperienceRepository = Depends(get_experience_repository),
) -> AddExperienceUseCase:
    """Get AddExperience use case."""
    return AddExperienceUseCase(experience_repo)


def get_instructor_dashboard_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> GetInstructorDashboardUseCase:
    """Get GetInstructorDashboard use case."""
    return GetInstructorDashboardUseCase(instructor_repo)


# Student Use Cases

def get_create_student_profile_use_case(
    student_repo: IStudentProfileRepository = Depends(get_student_repository),
) -> CreateStudentProfileUseCase:
    """Get CreateStudentProfile use case."""
    return CreateStudentProfileUseCase(student_repo)


def get_update_student_profile_use_case(
    student_repo: IStudentProfileRepository = Depends(get_student_repository),
) -> UpdateStudentProfileUseCase:
    """Get UpdateStudentProfile use case."""
    return UpdateStudentProfileUseCase(student_repo)


def get_record_session_completion_use_case(
    student_repo: IStudentProfileRepository = Depends(get_student_repository),
) -> RecordSessionCompletionUseCase:
    """Get RecordSessionCompletion use case."""
    return RecordSessionCompletionUseCase(student_repo)


# File Use Cases

def get_upload_file_use_case(
    file_repo: IFileRepository = Depends(get_file_repository),
) -> UploadFileUseCase:
    """Get UploadFile use case."""
    return UploadFileUseCase(file_repo)


def get_delete_file_use_case(
    file_repo: IFileRepository = Depends(get_file_repository),
) -> DeleteFileUseCase:
    """Get DeleteFile use case."""
    return DeleteFileUseCase(file_repo)


def get_get_file_use_case(
    file_repo: IFileRepository = Depends(get_file_repository),
) -> GetFileUseCase:
    """Get GetFile use case."""
    return GetFileUseCase(file_repo)


def get_list_user_files_use_case(
    file_repo: IFileRepository = Depends(get_file_repository),
) -> ListUserFilesUseCase:
    """Get ListUserFiles use case."""
    return ListUserFilesUseCase(file_repo)


# Scheduling Repository Dependencies

def get_availability_repository(db: Session = Depends(get_db)) -> IAvailabilityRepository:
    """Get Availability repository implementation."""
    return AvailabilityRepositoryImpl(db)


def get_session_repository(db: Session = Depends(get_db)) -> ISessionRepository:
    """Get Session repository implementation."""
    return SessionRepositoryImpl(db)


def get_time_off_repository(db: Session = Depends(get_db)) -> ITimeOffRepository:
    """Get TimeOff repository implementation."""
    return TimeOffRepositoryImpl(db)


def get_booking_slot_repository(db: Session = Depends(get_db)) -> IBookingSlotRepository:
    """Get BookingSlot repository implementation."""
    return BookingSlotRepositoryImpl(db)


# Scheduling Use Cases

def get_set_availability_use_case(
    availability_repo: IAvailabilityRepository = Depends(get_availability_repository),
    booking_slot_repo: IBookingSlotRepository = Depends(get_booking_slot_repository),
) -> SetAvailabilityUseCase:
    """Get SetAvailability use case."""
    return SetAvailabilityUseCase(availability_repo, booking_slot_repo)


def get_get_calendar_view_use_case(
    availability_repo: IAvailabilityRepository = Depends(get_availability_repository),
    session_repo: ISessionRepository = Depends(get_session_repository),
    time_off_repo: ITimeOffRepository = Depends(get_time_off_repository),
    booking_slot_repo: IBookingSlotRepository = Depends(get_booking_slot_repository),
) -> GetCalendarViewUseCase:
    """Get GetCalendarView use case."""
    return GetCalendarViewUseCase(availability_repo, session_repo, time_off_repo, booking_slot_repo)


def get_delete_availability_use_case(
    availability_repo: IAvailabilityRepository = Depends(get_availability_repository),
) -> DeleteAvailabilityUseCase:
    """Get DeleteAvailability use case."""
    return DeleteAvailabilityUseCase(availability_repo)


def get_update_availability_use_case(
    availability_repo: IAvailabilityRepository = Depends(get_availability_repository),
) -> UpdateAvailabilityUseCase:
    """Get UpdateAvailability use case."""
    return UpdateAvailabilityUseCase(availability_repo)


def get_add_time_off_use_case(
    time_off_repo: ITimeOffRepository = Depends(get_time_off_repository),
) -> AddTimeOffUseCase:
    """Get AddTimeOff use case."""
    return AddTimeOffUseCase(time_off_repo)


def get_delete_time_off_use_case(
    time_off_repo: ITimeOffRepository = Depends(get_time_off_repository),
) -> DeleteTimeOffUseCase:
    """Get DeleteTimeOff use case."""
    return DeleteTimeOffUseCase(time_off_repo)


def get_update_slot_use_case(
    booking_slot_repo: IBookingSlotRepository = Depends(get_booking_slot_repository),
    availability_repo: IAvailabilityRepository = Depends(get_availability_repository),
) -> UpdateSlotUseCase:
    """Get UpdateSlot use case."""
    return UpdateSlotUseCase(booking_slot_repo, availability_repo)


def get_delete_slot_use_case(
    booking_slot_repo: IBookingSlotRepository = Depends(get_booking_slot_repository),
) -> DeleteSlotUseCase:
    """Get DeleteSlot use case."""
    return DeleteSlotUseCase(booking_slot_repo)


# ============================================================================
# Authentication Dependencies
# ============================================================================


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Extract and verify JWT token from Authorization header.

    Args:
        credentials: HTTP bearer credentials

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user_allow_inactive(
    payload: dict = Depends(get_token_payload),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> User:
    """
    Get current authenticated user from JWT token (allows INACTIVE status).

    Use this for onboarding flows where users need access before activation.
    Still blocks suspended, banned, or deleted users.

    Args:
        payload: Decoded JWT token payload
        user_repo: User repository

    Returns:
        Current authenticated user (domain entity)

    Raises:
        HTTPException: If user not found or account is suspended/banned/deleted
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = user_repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Check for banned/suspended/deleted users only
    if user.status in [UserStatus.SUSPENDED, UserStatus.BANNED, UserStatus.DELETED]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account {user.status.value}",
        )

    return user


async def get_current_user(
    payload: dict = Depends(get_token_payload),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        payload: Decoded JWT token payload
        user_repo: User repository

    Returns:
        Current authenticated user (domain entity)

    Raises:
        HTTPException: If user not found or account inactive
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = user_repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account {user.status.value}",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account {current_user.status.value}",
        )
    return current_user


# ============================================================================
# Role-Based Access Control
# ============================================================================


async def get_current_instructor(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are an instructor."""
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor access required",
        )
    return current_user


async def get_current_instructor_allow_inactive(
    current_user: User = Depends(get_current_user_allow_inactive),
) -> User:
    """
    Get current user if they are an instructor (allows INACTIVE status).

    Use this for onboarding endpoints where instructors need access
    even if their account isn't fully activated yet.
    """
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor access required",
        )
    return current_user


async def get_current_student(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are a student."""
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required",
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ============================================================================
# Utility Functions
# ============================================================================


def get_password_hasher():
    """Get password hasher function."""
    return get_password_hash


def get_password_verifier():
    """Get password verifier function."""
    return verify_password
