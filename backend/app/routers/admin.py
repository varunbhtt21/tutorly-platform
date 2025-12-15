"""
Admin API Router.

Provides admin-only endpoints for:
- Dashboard statistics
- Instructor profile management (verify, reject, suspend)
- User management (suspend, ban, activate)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.domains.user.entities import User
from app.domains.user.value_objects import UserRole, UserStatus
from app.domains.instructor.value_objects import InstructorStatus
from app.core.dependencies import (
    get_current_admin,
    get_user_repository,
    get_instructor_repository,
    get_verify_instructor_use_case,
)
from app.domains.user.repositories import IUserRepository
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.application.use_cases.instructor import VerifyInstructorUseCase
from app.application.use_cases.admin import (
    RejectInstructorUseCase,
    SuspendInstructorUseCase,
    SuspendUserUseCase,
    BanUserUseCase,
    ActivateUserUseCase,
    GetPendingInstructorsUseCase,
    GetAdminDashboardStatsUseCase,
)


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class AdminDashboardStatsResponse(BaseModel):
    """Admin dashboard statistics response."""

    total_users: int
    total_students: int
    total_instructors: int
    total_admins: int
    active_users: int
    suspended_users: int
    banned_users: int
    pending_instructors: int
    verified_instructors: int
    rejected_instructors: int
    suspended_instructors: int


class UserResponse(BaseModel):
    """User response for admin views."""

    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    status: str
    email_verified: bool
    created_at: Optional[str]
    last_login_at: Optional[str]

    class Config:
        from_attributes = True


class InstructorProfileResponse(BaseModel):
    """Instructor profile response for admin views."""

    id: int
    user_id: int
    status: str
    headline: Optional[str]
    bio: Optional[str]
    country_of_birth: Optional[str]
    profile_photo_url: Optional[str]
    intro_video_url: Optional[str]
    onboarding_step: int
    is_onboarding_complete: bool
    created_at: Optional[str]


class PendingInstructorResponse(BaseModel):
    """Pending instructor with user details."""

    profile: InstructorProfileResponse
    user: UserResponse


class RejectInstructorRequest(BaseModel):
    """Request to reject instructor profile."""

    reason: str = Field(..., min_length=10, max_length=1000)


class SuspendRequest(BaseModel):
    """Request to suspend instructor or user."""

    reason: str = Field(..., min_length=10, max_length=1000)


class BanRequest(BaseModel):
    """Request to ban user."""

    reason: str = Field(..., min_length=10, max_length=1000)


class ActionResponse(BaseModel):
    """Generic action response."""

    success: bool
    message: str


# ============================================================================
# Dependency Injection for Use Cases
# ============================================================================


def get_reject_instructor_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> RejectInstructorUseCase:
    """Get RejectInstructor use case."""
    return RejectInstructorUseCase(instructor_repo)


def get_suspend_instructor_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> SuspendInstructorUseCase:
    """Get SuspendInstructor use case."""
    return SuspendInstructorUseCase(instructor_repo)


def get_suspend_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> SuspendUserUseCase:
    """Get SuspendUser use case."""
    return SuspendUserUseCase(user_repo)


def get_ban_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> BanUserUseCase:
    """Get BanUser use case."""
    return BanUserUseCase(user_repo)


def get_activate_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> ActivateUserUseCase:
    """Get ActivateUser use case."""
    return ActivateUserUseCase(user_repo)


def get_pending_instructors_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> GetPendingInstructorsUseCase:
    """Get GetPendingInstructors use case."""
    return GetPendingInstructorsUseCase(instructor_repo, user_repo)


def get_admin_dashboard_stats_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
) -> GetAdminDashboardStatsUseCase:
    """Get GetAdminDashboardStats use case."""
    return GetAdminDashboardStatsUseCase(user_repo, instructor_repo)


# ============================================================================
# Helper Functions
# ============================================================================


def user_to_response(user: User) -> UserResponse:
    """Convert User entity to response model."""
    return UserResponse(
        id=user.id,
        email=str(user.email),
        first_name=user.first_name,
        last_name=user.last_name,
        role=str(user.role),
        status=str(user.status),
        email_verified=user.email_verified,
        created_at=user.created_at.isoformat() if user.created_at else None,
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )


def instructor_profile_to_response(profile) -> InstructorProfileResponse:
    """Convert InstructorProfile entity to response model."""
    return InstructorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        status=str(profile.status),
        headline=profile.headline,
        bio=profile.bio,
        country_of_birth=profile.country_of_birth,
        profile_photo_url=profile.profile_photo_url,
        intro_video_url=profile.intro_video_url,
        onboarding_step=profile.onboarding_step,
        is_onboarding_complete=profile.is_onboarding_complete,
        created_at=profile.created_at.isoformat() if profile.created_at else None,
    )


# ============================================================================
# Dashboard Endpoints
# ============================================================================


@router.get("/dashboard/stats", response_model=AdminDashboardStatsResponse)
async def get_dashboard_stats(
    current_admin: User = Depends(get_current_admin),
    use_case: GetAdminDashboardStatsUseCase = Depends(get_admin_dashboard_stats_use_case),
):
    """
    Get admin dashboard statistics.

    Returns platform-wide statistics including user counts,
    instructor status counts, and moderation metrics.
    """
    stats = use_case.execute()
    return AdminDashboardStatsResponse(
        total_users=stats.total_users,
        total_students=stats.total_students,
        total_instructors=stats.total_instructors,
        total_admins=stats.total_admins,
        active_users=stats.active_users,
        suspended_users=stats.suspended_users,
        banned_users=stats.banned_users,
        pending_instructors=stats.pending_instructors,
        verified_instructors=stats.verified_instructors,
        rejected_instructors=stats.rejected_instructors,
        suspended_instructors=stats.suspended_instructors,
    )


# ============================================================================
# Instructor Management Endpoints
# ============================================================================


@router.get("/instructors/pending", response_model=List[PendingInstructorResponse])
async def get_pending_instructors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    use_case: GetPendingInstructorsUseCase = Depends(get_pending_instructors_use_case),
):
    """
    Get all instructor profiles pending review.

    Returns instructor profiles with PENDING_REVIEW status
    along with their user information for admin review.
    """
    results = use_case.execute(skip=skip, limit=limit)
    return [
        PendingInstructorResponse(
            profile=instructor_profile_to_response(profile),
            user=user_to_response(user),
        )
        for profile, user in results
    ]


@router.get("/instructors", response_model=List[PendingInstructorResponse])
async def get_all_instructors(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Get all instructor profiles with optional status filter.

    Admin can filter by instructor status: draft, pending_review, verified, rejected, suspended.
    """
    # Parse status filter
    instructor_status = None
    if status:
        try:
            instructor_status = InstructorStatus(status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in InstructorStatus]}",
            )

    # Get profiles
    profiles = instructor_repo.get_all(status=instructor_status, skip=skip, limit=limit)

    # Enrich with user data
    results = []
    for profile in profiles:
        user = user_repo.get_by_id(profile.user_id)
        if user:
            results.append(
                PendingInstructorResponse(
                    profile=instructor_profile_to_response(profile),
                    user=user_to_response(user),
                )
            )

    return results


@router.post("/instructors/{instructor_id}/verify", response_model=ActionResponse)
async def verify_instructor(
    instructor_id: int,
    current_admin: User = Depends(get_current_admin),
    use_case: VerifyInstructorUseCase = Depends(get_verify_instructor_use_case),
):
    """
    Verify an instructor profile.

    Transitions profile from PENDING_REVIEW to VERIFIED status.
    The instructor will be able to accept student bookings.
    """
    try:
        use_case.execute(instructor_id, current_admin.id)
        return ActionResponse(
            success=True,
            message=f"Instructor {instructor_id} has been verified successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/instructors/{instructor_id}/reject", response_model=ActionResponse)
async def reject_instructor(
    instructor_id: int,
    request: RejectInstructorRequest,
    current_admin: User = Depends(get_current_admin),
    use_case: RejectInstructorUseCase = Depends(get_reject_instructor_use_case),
):
    """
    Reject an instructor profile.

    Transitions profile from PENDING_REVIEW to REJECTED status.
    The instructor will receive the rejection reason and can
    update their profile to resubmit.
    """
    try:
        use_case.execute(instructor_id, request.reason, current_admin.id)
        return ActionResponse(
            success=True,
            message=f"Instructor {instructor_id} has been rejected",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/instructors/{instructor_id}/suspend", response_model=ActionResponse)
async def suspend_instructor(
    instructor_id: int,
    request: SuspendRequest,
    current_admin: User = Depends(get_current_admin),
    use_case: SuspendInstructorUseCase = Depends(get_suspend_instructor_use_case),
):
    """
    Suspend a verified instructor.

    Transitions profile from VERIFIED to SUSPENDED status.
    The instructor will not be able to accept new bookings.
    """
    try:
        use_case.execute(instructor_id, request.reason, current_admin.id)
        return ActionResponse(
            success=True,
            message=f"Instructor {instructor_id} has been suspended",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# User Management Endpoints
# ============================================================================


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    user_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Get all users with optional filters.

    Admin can filter by role (student, instructor, admin) and
    status (active, inactive, suspended, banned, deleted).
    """
    # Parse role filter
    user_role = None
    if role:
        try:
            user_role = UserRole(role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
            )

    # Parse status filter
    status_filter = None
    if user_status:
        try:
            status_filter = UserStatus(user_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in UserStatus]}",
            )

    # Get users
    users = user_repo.get_all(role=user_role, status=status_filter, skip=skip, limit=limit)
    return [user_to_response(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """Get a specific user by ID."""
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user_to_response(user)


@router.post("/users/{user_id}/suspend", response_model=ActionResponse)
async def suspend_user(
    user_id: int,
    request: SuspendRequest,
    current_admin: User = Depends(get_current_admin),
    use_case: SuspendUserUseCase = Depends(get_suspend_user_use_case),
):
    """
    Suspend a user account.

    The user will not be able to log in until activated.
    Cannot suspend admin users.
    """
    try:
        use_case.execute(user_id, request.reason)
        return ActionResponse(
            success=True,
            message=f"User {user_id} has been suspended",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/users/{user_id}/ban", response_model=ActionResponse)
async def ban_user(
    user_id: int,
    request: BanRequest,
    current_admin: User = Depends(get_current_admin),
    use_case: BanUserUseCase = Depends(get_ban_user_use_case),
):
    """
    Permanently ban a user account.

    The user will never be able to log in again.
    Cannot ban admin users.
    """
    try:
        use_case.execute(user_id, request.reason)
        return ActionResponse(
            success=True,
            message=f"User {user_id} has been banned",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/users/{user_id}/activate", response_model=ActionResponse)
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    use_case: ActivateUserUseCase = Depends(get_activate_user_use_case),
):
    """
    Activate a suspended or inactive user account.

    The user will be able to log in again.
    """
    try:
        use_case.execute(user_id)
        return ActionResponse(
            success=True,
            message=f"User {user_id} has been activated",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
