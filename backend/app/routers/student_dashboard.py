"""
Student Dashboard API Router.

Provides endpoints for the student dashboard features:
- Upcoming sessions
- Quick stats
- My instructors
- Session history
- Payment history
"""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.dependencies import (
    get_current_user,
    get_session_repository,
    get_payment_repository,
    get_instructor_repository,
    get_user_repository,
)
from app.domains.user.entities import User
from app.domains.scheduling.repositories import ISessionRepository
from app.domains.payment.repositories import IPaymentRepository
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.user.repositories import IUserRepository
from app.application.use_cases.student_dashboard import (
    GetStudentDashboardUseCase,
    StudentDashboardOutput,
)

router = APIRouter(prefix="/student/dashboard", tags=["student-dashboard"])


# ============================================================================
# Response Models
# ============================================================================

class UpcomingSessionResponse(BaseModel):
    """Response model for upcoming session."""
    session_id: int
    instructor_id: int
    instructor_name: str
    instructor_photo_url: Optional[str] = None
    subject: Optional[str] = None
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    session_type: str
    status: str
    meeting_link: Optional[str] = None
    timezone: str
    can_join: bool
    can_cancel: bool
    can_reschedule: bool
    amount: float
    currency: str

    class Config:
        from_attributes = True


class StudentStatsResponse(BaseModel):
    """Response model for student statistics."""
    total_sessions_completed: int
    total_hours_learning: float
    current_streak_weeks: int
    total_spent: float
    currency: str
    total_instructors: int
    trial_sessions_used: int

    class Config:
        from_attributes = True


class MyInstructorResponse(BaseModel):
    """Response model for instructor the student has worked with."""
    instructor_id: int
    user_id: int
    name: str
    photo_url: Optional[str] = None
    headline: Optional[str] = None
    total_sessions_with: int
    last_session_date: Optional[datetime] = None
    average_rating: Optional[float] = None
    regular_session_price: Optional[float] = None
    trial_session_price: Optional[float] = None
    currency: str

    class Config:
        from_attributes = True


class SessionHistoryResponse(BaseModel):
    """Response model for session history."""
    session_id: int
    instructor_id: int
    instructor_name: str
    instructor_photo_url: Optional[str] = None
    subject: Optional[str] = None
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    session_type: str
    status: str
    amount: float
    currency: str
    can_review: bool
    has_review: bool
    instructor_notes: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentHistoryResponse(BaseModel):
    """Response model for payment history."""
    payment_id: int
    instructor_name: str
    amount: float
    currency: str
    status: str
    lesson_type: str
    payment_method: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    session_id: Optional[int] = None
    session_date: Optional[datetime] = None
    refund_status: Optional[str] = None

    class Config:
        from_attributes = True


class StudentDashboardResponse(BaseModel):
    """Complete student dashboard response."""
    upcoming_sessions: List[UpcomingSessionResponse]
    stats: StudentStatsResponse
    my_instructors: List[MyInstructorResponse]
    session_history: List[SessionHistoryResponse]
    payment_history: List[PaymentHistoryResponse]

    class Config:
        from_attributes = True


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=StudentDashboardResponse)
async def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Get complete student dashboard data.

    Returns all sections of the student dashboard:
    - Upcoming sessions (next 7 days)
    - Quick stats (completed sessions, hours, streak, spending)
    - My instructors (instructors the student has booked with)
    - Session history (past sessions)
    - Payment history (recent transactions)
    """
    # Verify user is a student
    if current_user.role.value not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access the student dashboard"
        )

    # Execute use case
    use_case = GetStudentDashboardUseCase(
        session_repo=session_repo,
        payment_repo=payment_repo,
        instructor_repo=instructor_repo,
        user_repo=user_repo,
    )

    result = use_case.execute(student_id=current_user.id)

    # Convert to response models
    return StudentDashboardResponse(
        upcoming_sessions=[
            UpcomingSessionResponse(
                session_id=s.session_id,
                instructor_id=s.instructor_id,
                instructor_name=s.instructor_name,
                instructor_photo_url=s.instructor_photo_url,
                subject=s.subject,
                start_at=s.start_at,
                end_at=s.end_at,
                duration_minutes=s.duration_minutes,
                session_type=s.session_type,
                status=s.status,
                meeting_link=s.meeting_link,
                timezone=s.timezone,
                can_join=s.can_join,
                can_cancel=s.can_cancel,
                can_reschedule=s.can_reschedule,
                amount=float(s.amount),
                currency=s.currency,
            )
            for s in result.upcoming_sessions
        ],
        stats=StudentStatsResponse(
            total_sessions_completed=result.stats.total_sessions_completed,
            total_hours_learning=result.stats.total_hours_learning,
            current_streak_weeks=result.stats.current_streak_weeks,
            total_spent=float(result.stats.total_spent),
            currency=result.stats.currency,
            total_instructors=result.stats.total_instructors,
            trial_sessions_used=result.stats.trial_sessions_used,
        ) if result.stats else StudentStatsResponse(
            total_sessions_completed=0,
            total_hours_learning=0,
            current_streak_weeks=0,
            total_spent=0,
            currency="INR",
            total_instructors=0,
            trial_sessions_used=0,
        ),
        my_instructors=[
            MyInstructorResponse(
                instructor_id=i.instructor_id,
                user_id=i.user_id,
                name=i.name,
                photo_url=i.photo_url,
                headline=i.headline,
                total_sessions_with=i.total_sessions_with,
                last_session_date=i.last_session_date,
                average_rating=i.average_rating,
                regular_session_price=float(i.regular_session_price) if i.regular_session_price else None,
                trial_session_price=float(i.trial_session_price) if i.trial_session_price else None,
                currency=i.currency,
            )
            for i in result.my_instructors
        ],
        session_history=[
            SessionHistoryResponse(
                session_id=s.session_id,
                instructor_id=s.instructor_id,
                instructor_name=s.instructor_name,
                instructor_photo_url=s.instructor_photo_url,
                subject=s.subject,
                start_at=s.start_at,
                end_at=s.end_at,
                duration_minutes=s.duration_minutes,
                session_type=s.session_type,
                status=s.status,
                amount=float(s.amount),
                currency=s.currency,
                can_review=s.can_review,
                has_review=s.has_review,
                instructor_notes=s.instructor_notes,
            )
            for s in result.session_history
        ],
        payment_history=[
            PaymentHistoryResponse(
                payment_id=p.payment_id,
                instructor_name=p.instructor_name,
                amount=float(p.amount),
                currency=p.currency,
                status=p.status,
                lesson_type=p.lesson_type,
                payment_method=p.payment_method,
                created_at=p.created_at,
                completed_at=p.completed_at,
                session_id=p.session_id,
                session_date=p.session_date,
                refund_status=p.refund_status,
            )
            for p in result.payment_history
        ],
    )


@router.get("/upcoming-sessions", response_model=List[UpcomingSessionResponse])
async def get_upcoming_sessions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
):
    """Get only upcoming sessions for the student."""
    if current_user.role.value not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    use_case = GetStudentDashboardUseCase(
        session_repo=session_repo,
        payment_repo=payment_repo,
        instructor_repo=instructor_repo,
        user_repo=user_repo,
    )

    result = use_case.execute(student_id=current_user.id)

    return [
        UpcomingSessionResponse(
            session_id=s.session_id,
            instructor_id=s.instructor_id,
            instructor_name=s.instructor_name,
            instructor_photo_url=s.instructor_photo_url,
            subject=s.subject,
            start_at=s.start_at,
            end_at=s.end_at,
            duration_minutes=s.duration_minutes,
            session_type=s.session_type,
            status=s.status,
            meeting_link=s.meeting_link,
            timezone=s.timezone,
            can_join=s.can_join,
            can_cancel=s.can_cancel,
            can_reschedule=s.can_reschedule,
            amount=float(s.amount),
            currency=s.currency,
        )
        for s in result.upcoming_sessions[:limit]
    ]


@router.get("/stats", response_model=StudentStatsResponse)
async def get_student_stats(
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """Get only student statistics."""
    if current_user.role.value not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    use_case = GetStudentDashboardUseCase(
        session_repo=session_repo,
        payment_repo=payment_repo,
        instructor_repo=instructor_repo,
        user_repo=user_repo,
    )

    result = use_case.execute(student_id=current_user.id)

    return StudentStatsResponse(
        total_sessions_completed=result.stats.total_sessions_completed,
        total_hours_learning=result.stats.total_hours_learning,
        current_streak_weeks=result.stats.current_streak_weeks,
        total_spent=float(result.stats.total_spent),
        currency=result.stats.currency,
        total_instructors=result.stats.total_instructors,
        trial_sessions_used=result.stats.trial_sessions_used,
    )


@router.get("/my-instructors", response_model=List[MyInstructorResponse])
async def get_my_instructors(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """Get instructors the student has booked with."""
    if current_user.role.value not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    use_case = GetStudentDashboardUseCase(
        session_repo=session_repo,
        payment_repo=payment_repo,
        instructor_repo=instructor_repo,
        user_repo=user_repo,
    )

    result = use_case.execute(student_id=current_user.id)

    return [
        MyInstructorResponse(
            instructor_id=i.instructor_id,
            user_id=i.user_id,
            name=i.name,
            photo_url=i.photo_url,
            headline=i.headline,
            total_sessions_with=i.total_sessions_with,
            last_session_date=i.last_session_date,
            average_rating=i.average_rating,
            regular_session_price=float(i.regular_session_price) if i.regular_session_price else None,
            trial_session_price=float(i.trial_session_price) if i.trial_session_price else None,
            currency=i.currency,
        )
        for i in result.my_instructors[:limit]
    ]


@router.get("/session-history", response_model=List[SessionHistoryResponse])
async def get_session_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """Get session history for the student."""
    if current_user.role.value not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    use_case = GetStudentDashboardUseCase(
        session_repo=session_repo,
        payment_repo=payment_repo,
        instructor_repo=instructor_repo,
        user_repo=user_repo,
    )

    result = use_case.execute(student_id=current_user.id)

    return [
        SessionHistoryResponse(
            session_id=s.session_id,
            instructor_id=s.instructor_id,
            instructor_name=s.instructor_name,
            instructor_photo_url=s.instructor_photo_url,
            subject=s.subject,
            start_at=s.start_at,
            end_at=s.end_at,
            duration_minutes=s.duration_minutes,
            session_type=s.session_type,
            status=s.status,
            amount=float(s.amount),
            currency=s.currency,
            can_review=s.can_review,
            has_review=s.has_review,
            instructor_notes=s.instructor_notes,
        )
        for s in result.session_history[offset:offset + limit]
    ]


@router.get("/payment-history", response_model=List[PaymentHistoryResponse])
async def get_payment_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """Get payment history for the student."""
    if current_user.role.value not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    use_case = GetStudentDashboardUseCase(
        session_repo=session_repo,
        payment_repo=payment_repo,
        instructor_repo=instructor_repo,
        user_repo=user_repo,
    )

    result = use_case.execute(student_id=current_user.id)

    return [
        PaymentHistoryResponse(
            payment_id=p.payment_id,
            instructor_name=p.instructor_name,
            amount=float(p.amount),
            currency=p.currency,
            status=p.status,
            lesson_type=p.lesson_type,
            payment_method=p.payment_method,
            created_at=p.created_at,
            completed_at=p.completed_at,
            session_id=p.session_id,
            session_date=p.session_date,
            refund_status=p.refund_status,
        )
        for p in result.payment_history[offset:offset + limit]
    ]
