"""Session entity for scheduling domain."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from ..value_objects import SessionStatus, SessionType


@dataclass
class Session:
    """
    Aggregate root representing a booked tutoring session.

    Manages the full lifecycle of a session from booking to completion.
    """
    instructor_id: int
    student_id: int
    start_at: datetime
    end_at: datetime
    session_type: SessionType
    status: SessionStatus = SessionStatus.PENDING_CONFIRMATION
    timezone: str = "UTC"

    # Subject and pricing
    subject_id: Optional[int] = None
    amount: Decimal = Decimal("0.00")
    currency: str = "USD"

    # Recurrence info (for weekly lessons)
    parent_session_id: Optional[int] = None
    recurrence_pattern: Optional[str] = None  # 'weekly'
    occurrence_number: int = 1

    # Notes and meeting
    instructor_notes: Optional[str] = None
    student_notes: Optional[str] = None
    meeting_link: Optional[str] = None

    # Cancellation info
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancellation_reason: Optional[str] = None

    # Identity
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate session after initialization."""
        self._validate()

    def _validate(self):
        """Validate session configuration."""
        if self.start_at >= self.end_at:
            raise ValueError("Start time must be before end time")

        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    @property
    def duration_minutes(self) -> int:
        """Get session duration in minutes."""
        return int((self.end_at - self.start_at).total_seconds() / 60)

    @property
    def is_trial(self) -> bool:
        """Check if this is a trial session."""
        return self.session_type == SessionType.TRIAL

    @property
    def is_recurring(self) -> bool:
        """Check if this is part of a recurring series."""
        return self.session_type == SessionType.RECURRING

    @property
    def is_active(self) -> bool:
        """Check if session is in an active state."""
        return self.status.is_active

    @property
    def is_completed(self) -> bool:
        """Check if session is completed."""
        return self.status == SessionStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if session is cancelled."""
        return self.status == SessionStatus.CANCELLED

    @property
    def can_be_cancelled(self) -> bool:
        """Check if session can still be cancelled."""
        if not self.status.can_be_cancelled:
            return False
        # Allow cancellation up to 24 hours before
        return datetime.utcnow() < self.start_at - timedelta(hours=24)

    @property
    def can_be_rescheduled(self) -> bool:
        """Check if session can be rescheduled."""
        if not self.status.can_be_rescheduled:
            return False
        # Allow reschedule up to 24 hours before
        return datetime.utcnow() < self.start_at - timedelta(hours=24)

    @property
    def can_be_joined(self) -> bool:
        """
        Check if session can be joined.

        A session can be joined when:
        1. Session is CONFIRMED or IN_PROGRESS (active sessions)
        2. Current time is within the join window:
           - From 15 minutes before start time (early entry allowed)
           - Until the scheduled end time of the session

        Students can join and wait in the classroom regardless of whether
        the instructor has joined yet. The "Enter Classroom" button remains
        available throughout the session duration.

        This encapsulates the business rule for join eligibility,
        following the same pattern as can_be_cancelled and can_be_rescheduled.
        """
        now = datetime.utcnow()

        # Only confirmed or in-progress sessions can be joined
        if self.status not in (SessionStatus.CONFIRMED, SessionStatus.IN_PROGRESS):
            return False

        # Calculate time window
        time_to_session_minutes = (self.start_at - now).total_seconds() / 60

        # Allow join from 15 minutes before start until session end time
        # -15 means 15 mins before (negative because start_at is in future)
        # duration_minutes is the max time after start (session end)
        return -15 <= time_to_session_minutes <= self.duration_minutes

    def confirm(self):
        """Confirm the session."""
        if self.status != SessionStatus.PENDING_CONFIRMATION:
            raise ValueError(f"Cannot confirm session in {self.status.value} status")
        self.status = SessionStatus.CONFIRMED
        self.updated_at = datetime.utcnow()

    def start(self):
        """Start the session."""
        if self.status != SessionStatus.CONFIRMED:
            raise ValueError(f"Cannot start session in {self.status.value} status")
        self.status = SessionStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def complete(self):
        """Mark session as completed."""
        if self.status not in (SessionStatus.CONFIRMED, SessionStatus.IN_PROGRESS):
            raise ValueError(f"Cannot complete session in {self.status.value} status")
        self.status = SessionStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def cancel(self, cancelled_by: int, reason: Optional[str] = None):
        """Cancel the session."""
        if not self.status.can_be_cancelled:
            raise ValueError(f"Cannot cancel session in {self.status.value} status")
        self.status = SessionStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()

    def mark_no_show(self):
        """Mark session as no-show."""
        if self.status != SessionStatus.CONFIRMED:
            raise ValueError(f"Cannot mark no-show for session in {self.status.value} status")
        self.status = SessionStatus.NO_SHOW
        self.updated_at = datetime.utcnow()

    def reschedule(self, new_start: datetime, new_end: datetime):
        """Reschedule the session to a new time."""
        if not self.can_be_rescheduled:
            raise ValueError("Session cannot be rescheduled")

        if new_start >= new_end:
            raise ValueError("New start time must be before new end time")

        self.start_at = new_start
        self.end_at = new_end
        self.status = SessionStatus.PENDING_CONFIRMATION  # Requires re-confirmation
        self.updated_at = datetime.utcnow()

    def set_meeting_link(self, link: str):
        """Set the meeting link."""
        self.meeting_link = link
        self.updated_at = datetime.utcnow()

    def add_instructor_notes(self, notes: str):
        """Add or update instructor notes."""
        self.instructor_notes = notes
        self.updated_at = datetime.utcnow()

    def add_student_notes(self, notes: str):
        """Add or update student notes."""
        self.student_notes = notes
        self.updated_at = datetime.utcnow()

    @classmethod
    def book_trial(
        cls,
        instructor_id: int,
        student_id: int,
        start_at: datetime,
        duration_minutes: int,
        amount: Decimal,
        timezone: str = "UTC",
        subject_id: Optional[int] = None,
    ) -> "Session":
        """Factory method for booking a trial session."""
        return cls(
            instructor_id=instructor_id,
            student_id=student_id,
            start_at=start_at,
            end_at=start_at + timedelta(minutes=duration_minutes),
            session_type=SessionType.TRIAL,
            timezone=timezone,
            subject_id=subject_id,
            amount=amount,
        )

    @classmethod
    def book_single(
        cls,
        instructor_id: int,
        student_id: int,
        start_at: datetime,
        duration_minutes: int,
        amount: Decimal,
        timezone: str = "UTC",
        subject_id: Optional[int] = None,
    ) -> "Session":
        """Factory method for booking a single session."""
        return cls(
            instructor_id=instructor_id,
            student_id=student_id,
            start_at=start_at,
            end_at=start_at + timedelta(minutes=duration_minutes),
            session_type=SessionType.SINGLE,
            timezone=timezone,
            subject_id=subject_id,
            amount=amount,
        )

    @classmethod
    def book_recurring(
        cls,
        instructor_id: int,
        student_id: int,
        start_at: datetime,
        duration_minutes: int,
        amount: Decimal,
        parent_session_id: Optional[int] = None,
        occurrence_number: int = 1,
        timezone: str = "UTC",
        subject_id: Optional[int] = None,
    ) -> "Session":
        """Factory method for booking a recurring session."""
        return cls(
            instructor_id=instructor_id,
            student_id=student_id,
            start_at=start_at,
            end_at=start_at + timedelta(minutes=duration_minutes),
            session_type=SessionType.RECURRING,
            recurrence_pattern="weekly",
            parent_session_id=parent_session_id,
            occurrence_number=occurrence_number,
            timezone=timezone,
            subject_id=subject_id,
            amount=amount,
        )

    def __repr__(self) -> str:
        return f"Session({self.session_type.value}, {self.start_at}, {self.status.value})"
