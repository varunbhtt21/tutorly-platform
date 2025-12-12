"""SQLAlchemy models for scheduling domain."""

from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Time, Boolean,
    ForeignKey, Numeric, Text, Index
)
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.database import Base


class AvailabilitySlot(Base):
    """SQLAlchemy model for instructor availability slots."""

    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type: 'recurring' or 'one_time'
    availability_type = Column(String(20), nullable=False)

    # For recurring availability
    day_of_week = Column(Integer, nullable=True)  # 0=Monday, 6=Sunday

    # Time window
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # For one-time availability
    specific_date = Column(Date, nullable=True)

    # Slot configuration
    slot_duration_minutes = Column(Integer, default=50)
    break_minutes = Column(Integer, default=10)

    # Validity period for recurring
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)

    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_availability_instructor_day', 'instructor_id', 'day_of_week'),
        Index('idx_availability_instructor_date', 'instructor_id', 'specific_date'),
        Index('idx_availability_active', 'instructor_id', 'is_active'),
    )


class Session(Base):
    """SQLAlchemy model for booked tutoring sessions."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Timing
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    timezone = Column(String(50), default="UTC")

    # Type and status
    session_type = Column(String(20), nullable=False)  # trial, single, recurring
    status = Column(String(30), nullable=False, default="pending_confirmation")

    # Recurrence (for weekly lessons)
    parent_session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    recurrence_pattern = Column(String(20), nullable=True)  # 'weekly'
    occurrence_number = Column(Integer, default=1)

    # Subject and pricing
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")

    # Notes and meeting
    instructor_notes = Column(Text, nullable=True)
    student_notes = Column(Text, nullable=True)
    meeting_link = Column(String(500), nullable=True)

    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = relationship("Session", backref="parent", remote_side=[id])

    # Indexes
    __table_args__ = (
        Index('idx_sessions_instructor_time', 'instructor_id', 'start_at'),
        Index('idx_sessions_student_time', 'student_id', 'start_at'),
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_instructor_status', 'instructor_id', 'status'),
    )


class BookingSlot(Base):
    """SQLAlchemy model for individual bookable time slots."""

    __tablename__ = "booking_slots"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Reference to the availability rule that created this slot (optional)
    availability_rule_id = Column(
        Integer,
        ForeignKey("availability_slots.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Exact timing for this slot
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=50)

    # Status: available, booked, blocked
    status = Column(String(20), nullable=False, default="available")

    # If booked, link to the session
    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_booking_slots_instructor_time', 'instructor_id', 'start_at'),
        Index('idx_booking_slots_instructor_status', 'instructor_id', 'status'),
        Index('idx_booking_slots_rule', 'availability_rule_id'),
    )


class TimeOff(Base):
    """SQLAlchemy model for instructor time off / blocked time."""

    __tablename__ = "time_off"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)

    # For recurring weekly blocks
    is_recurring = Column(Boolean, default=False)
    recurrence_day = Column(Integer, nullable=True)  # 0=Monday, 6=Sunday

    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_time_off_instructor_dates', 'instructor_id', 'start_at', 'end_at'),
    )
