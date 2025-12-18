"""
Get Student Dashboard Use Case.

Aggregates all data needed for the student dashboard in a single optimized query.
Following DDD principles with clear separation of concerns.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Set

from app.domains.scheduling.repositories import ISessionRepository
from app.domains.scheduling.value_objects import SessionStatus
from app.domains.payment.repositories import IPaymentRepository
from app.domains.payment.value_objects.enums import PaymentStatus
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.user.repositories import IUserRepository


@dataclass
class UpcomingSessionDTO:
    """Data transfer object for upcoming session."""
    session_id: int
    instructor_id: int
    instructor_name: str
    instructor_photo_url: Optional[str]
    subject: Optional[str]
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    session_type: str  # trial, single, recurring
    status: str
    meeting_link: Optional[str]
    timezone: str
    can_join: bool  # True if within 5 mins of start time
    can_cancel: bool
    can_reschedule: bool
    amount: Decimal
    currency: str


@dataclass
class StudentStatsDTO:
    """Data transfer object for student statistics."""
    total_sessions_completed: int
    total_hours_learning: float
    current_streak_weeks: int
    total_spent: Decimal
    currency: str
    total_instructors: int
    trial_sessions_used: int


@dataclass
class MyInstructorDTO:
    """Data transfer object for instructor the student has booked with."""
    instructor_id: int
    user_id: int
    name: str
    photo_url: Optional[str]
    headline: Optional[str]
    total_sessions_with: int
    last_session_date: Optional[datetime]
    average_rating: Optional[float]
    regular_session_price: Optional[Decimal]
    trial_session_price: Optional[Decimal]
    currency: str


@dataclass
class SessionHistoryDTO:
    """Data transfer object for session history."""
    session_id: int
    instructor_id: int
    instructor_name: str
    instructor_photo_url: Optional[str]
    subject: Optional[str]
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    session_type: str
    status: str  # completed, cancelled, no_show
    amount: Decimal
    currency: str
    can_review: bool  # True if completed and not reviewed yet
    has_review: bool
    instructor_notes: Optional[str]


@dataclass
class PaymentHistoryDTO:
    """Data transfer object for payment history."""
    payment_id: int
    instructor_name: str
    amount: Decimal
    currency: str
    status: str  # completed, refunded, failed
    lesson_type: str  # trial, regular
    payment_method: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    session_id: Optional[int]
    session_date: Optional[datetime]
    refund_status: Optional[str]


@dataclass
class StudentDashboardOutput:
    """Complete student dashboard data."""
    # Section 1: Upcoming Sessions
    upcoming_sessions: List[UpcomingSessionDTO] = field(default_factory=list)

    # Section 2: Quick Stats
    stats: Optional[StudentStatsDTO] = None

    # Section 3: My Instructors
    my_instructors: List[MyInstructorDTO] = field(default_factory=list)

    # Section 4: Session History (recent past sessions)
    session_history: List[SessionHistoryDTO] = field(default_factory=list)

    # Section 5: Payment History (recent payments)
    payment_history: List[PaymentHistoryDTO] = field(default_factory=list)


class GetStudentDashboardUseCase:
    """
    Use case for getting all student dashboard data.

    Aggregates data from multiple repositories to provide a complete
    dashboard view in a single use case execution.
    """

    def __init__(
        self,
        session_repo: ISessionRepository,
        payment_repo: IPaymentRepository,
        instructor_repo: IInstructorProfileRepository,
        user_repo: IUserRepository,
    ):
        """
        Initialize use case with required repositories.

        Args:
            session_repo: Session repository for booking data
            payment_repo: Payment repository for transaction data
            instructor_repo: Instructor repository for instructor data
            user_repo: User repository for user details
        """
        self.session_repo = session_repo
        self.payment_repo = payment_repo
        self.instructor_repo = instructor_repo
        self.user_repo = user_repo

    def execute(self, student_id: int) -> StudentDashboardOutput:
        """
        Execute the use case to get complete dashboard data.

        Args:
            student_id: The student's user ID

        Returns:
            StudentDashboardOutput with all dashboard sections populated
        """
        # Get upcoming sessions (next 7 days)
        upcoming_sessions = self._get_upcoming_sessions(student_id)

        # Get student statistics
        stats = self._get_student_stats(student_id)

        # Get instructors the student has booked with
        my_instructors = self._get_my_instructors(student_id)

        # Get session history (past sessions)
        session_history = self._get_session_history(student_id)

        # Get payment history
        payment_history = self._get_payment_history(student_id)

        return StudentDashboardOutput(
            upcoming_sessions=upcoming_sessions,
            stats=stats,
            my_instructors=my_instructors,
            session_history=session_history,
            payment_history=payment_history,
        )

    def _get_upcoming_sessions(self, student_id: int) -> List[UpcomingSessionDTO]:
        """Get upcoming sessions for the next 7 days."""
        now = datetime.utcnow()
        end_date = (now + timedelta(days=7)).date()

        # Get upcoming sessions
        sessions = self.session_repo.get_upcoming_by_student(student_id, limit=20)

        # Build instructor cache to avoid N+1 queries
        instructor_ids = {s.instructor_id for s in sessions}
        instructor_cache = self._build_instructor_cache(instructor_ids)

        upcoming = []
        for session in sessions:
            instructor = instructor_cache.get(session.instructor_id)
            if not instructor:
                continue

            # Check if can join (within 5 mins of start)
            time_to_session = (session.start_at - now).total_seconds() / 60
            can_join = -5 <= time_to_session <= session.duration_minutes

            upcoming.append(UpcomingSessionDTO(
                session_id=session.id,
                instructor_id=session.instructor_id,
                instructor_name=instructor.get("name", "Unknown"),
                instructor_photo_url=instructor.get("photo_url"),
                subject=None,  # TODO: Add subject lookup
                start_at=session.start_at,
                end_at=session.end_at,
                duration_minutes=session.duration_minutes,
                session_type=session.session_type.value,
                status=session.status.value,
                meeting_link=session.meeting_link,
                timezone=session.timezone,
                can_join=can_join,
                can_cancel=session.can_be_cancelled,
                can_reschedule=session.can_be_rescheduled,
                amount=session.amount,
                currency=session.currency,
            ))

        return upcoming

    def _get_student_stats(self, student_id: int) -> StudentStatsDTO:
        """Calculate student statistics."""
        now = datetime.utcnow()

        # Get all completed sessions
        completed_sessions = self.session_repo.get_by_student(
            student_id=student_id,
            status=SessionStatus.COMPLETED,
        )

        # Calculate total hours
        total_minutes = sum(s.duration_minutes for s in completed_sessions)
        total_hours = total_minutes / 60

        # Calculate total spent from completed payments
        payments = self.payment_repo.get_by_student_id(
            student_id=student_id,
            status=PaymentStatus.COMPLETED,
            limit=1000,
        )
        total_spent = sum(p.amount for p in payments)

        # Get unique instructors
        unique_instructors = {s.instructor_id for s in completed_sessions}

        # Count trial sessions
        trial_sessions = sum(1 for s in completed_sessions if s.is_trial)

        # Calculate streak (consecutive weeks with sessions)
        streak = self._calculate_streak(completed_sessions)

        return StudentStatsDTO(
            total_sessions_completed=len(completed_sessions),
            total_hours_learning=round(total_hours, 1),
            current_streak_weeks=streak,
            total_spent=total_spent,
            currency="INR",
            total_instructors=len(unique_instructors),
            trial_sessions_used=trial_sessions,
        )

    def _calculate_streak(self, sessions: list) -> int:
        """Calculate consecutive weeks with at least one session."""
        if not sessions:
            return 0

        # Get weeks with sessions
        weeks_with_sessions: Set[tuple] = set()
        for session in sessions:
            # Get ISO week (year, week_number)
            iso_cal = session.start_at.isocalendar()
            weeks_with_sessions.add((iso_cal[0], iso_cal[1]))

        if not weeks_with_sessions:
            return 0

        # Get current week
        now = datetime.utcnow()
        current_iso = now.isocalendar()
        current_week = (current_iso[0], current_iso[1])

        # Count consecutive weeks going backward from current
        streak = 0
        check_week = current_week

        while check_week in weeks_with_sessions:
            streak += 1
            # Go to previous week
            prev_date = datetime.fromisocalendar(check_week[0], check_week[1], 1) - timedelta(days=7)
            prev_iso = prev_date.isocalendar()
            check_week = (prev_iso[0], prev_iso[1])

        return streak

    def _get_my_instructors(self, student_id: int) -> List[MyInstructorDTO]:
        """Get instructors the student has booked with."""
        # Get all sessions for the student
        all_sessions = self.session_repo.get_by_student(student_id=student_id)

        # Group by instructor
        instructor_sessions: Dict[int, list] = {}
        for session in all_sessions:
            if session.instructor_id not in instructor_sessions:
                instructor_sessions[session.instructor_id] = []
            instructor_sessions[session.instructor_id].append(session)

        # Build instructor cache
        instructor_cache = self._build_instructor_cache(set(instructor_sessions.keys()))

        instructors = []
        for instructor_id, sessions in instructor_sessions.items():
            instructor = instructor_cache.get(instructor_id)
            if not instructor:
                continue

            # Get last session date
            completed_sessions = [s for s in sessions if s.status == SessionStatus.COMPLETED]
            last_session = max(completed_sessions, key=lambda x: x.start_at) if completed_sessions else None

            instructors.append(MyInstructorDTO(
                instructor_id=instructor_id,
                user_id=instructor.get("user_id", 0),
                name=instructor.get("name", "Unknown"),
                photo_url=instructor.get("photo_url"),
                headline=instructor.get("headline"),
                total_sessions_with=len(sessions),
                last_session_date=last_session.start_at if last_session else None,
                average_rating=instructor.get("average_rating"),
                regular_session_price=instructor.get("regular_session_price"),
                trial_session_price=instructor.get("trial_session_price"),
                currency="INR",
            ))

        # Sort by last session date (most recent first)
        instructors.sort(
            key=lambda x: x.last_session_date or datetime.min,
            reverse=True
        )

        return instructors[:10]  # Limit to top 10

    def _get_session_history(self, student_id: int) -> List[SessionHistoryDTO]:
        """Get past sessions (completed, cancelled, no-show)."""
        now = datetime.utcnow()

        # Get all past sessions
        all_sessions = self.session_repo.get_by_student(student_id=student_id)

        # Filter to past sessions with final statuses
        past_sessions = [
            s for s in all_sessions
            if s.status in (
                SessionStatus.COMPLETED,
                SessionStatus.CANCELLED,
                SessionStatus.NO_SHOW,
            ) or s.end_at < now
        ]

        # Sort by start time descending (most recent first)
        past_sessions.sort(key=lambda x: x.start_at, reverse=True)
        past_sessions = past_sessions[:20]  # Limit to 20

        # Build instructor cache
        instructor_ids = {s.instructor_id for s in past_sessions}
        instructor_cache = self._build_instructor_cache(instructor_ids)

        history = []
        for session in past_sessions:
            instructor = instructor_cache.get(session.instructor_id)
            if not instructor:
                continue

            # TODO: Check if session has review
            has_review = False  # Placeholder - would need review repository

            history.append(SessionHistoryDTO(
                session_id=session.id,
                instructor_id=session.instructor_id,
                instructor_name=instructor.get("name", "Unknown"),
                instructor_photo_url=instructor.get("photo_url"),
                subject=None,  # TODO: Add subject lookup
                start_at=session.start_at,
                end_at=session.end_at,
                duration_minutes=session.duration_minutes,
                session_type=session.session_type.value,
                status=session.status.value,
                amount=session.amount,
                currency=session.currency,
                can_review=session.status == SessionStatus.COMPLETED and not has_review,
                has_review=has_review,
                instructor_notes=session.instructor_notes,
            ))

        return history

    def _get_payment_history(self, student_id: int) -> List[PaymentHistoryDTO]:
        """Get payment history."""
        # Get recent payments
        payments = self.payment_repo.get_by_student_id(
            student_id=student_id,
            limit=20,
        )

        # Build instructor cache from payments
        instructor_user_ids = {p.instructor_id for p in payments}
        user_cache = {}
        for user_id in instructor_user_ids:
            user = self.user_repo.get_by_id(user_id)
            if user:
                user_cache[user_id] = f"{user.first_name} {user.last_name}"

        history = []
        for payment in payments:
            instructor_name = user_cache.get(payment.instructor_id, "Unknown")

            # Get session date if available
            session_date = None
            if payment.session_id:
                session = self.session_repo.get_by_id(payment.session_id)
                if session:
                    session_date = session.start_at

            history.append(PaymentHistoryDTO(
                payment_id=payment.id,
                instructor_name=instructor_name,
                amount=payment.amount,
                currency=payment.currency,
                status=payment.status.value,
                lesson_type=payment.lesson_type.value,
                payment_method=payment.payment_method.value if payment.payment_method else None,
                created_at=payment.created_at,
                completed_at=payment.completed_at,
                session_id=payment.session_id,
                session_date=session_date,
                refund_status="refunded" if payment.status == PaymentStatus.REFUNDED else None,
            ))

        return history

    def _build_instructor_cache(self, instructor_ids: Set[int]) -> Dict[int, dict]:
        """Build a cache of instructor data to avoid N+1 queries."""
        cache = {}

        for instructor_id in instructor_ids:
            profile = self.instructor_repo.get_by_id(instructor_id)
            if not profile:
                continue

            # Get user for name
            user = self.user_repo.get_by_id(profile.user_id)
            if not user:
                continue

            # Extract rating from Rating value object
            average_rating = None
            if profile.rating and profile.rating.total_reviews > 0:
                average_rating = float(profile.rating.average_score)

            # Extract pricing from Pricing value object
            regular_session_price = None
            trial_session_price = None
            if profile.pricing:
                regular_session_price = profile.pricing.regular_session_price
                trial_session_price = profile.pricing.trial_session_price

            cache[instructor_id] = {
                "user_id": profile.user_id,
                "name": f"{user.first_name} {user.last_name}",
                "photo_url": profile.profile_photo_url,
                "headline": profile.headline,
                "average_rating": average_rating,
                "regular_session_price": regular_session_price,
                "trial_session_price": trial_session_price,
            }

        return cache
