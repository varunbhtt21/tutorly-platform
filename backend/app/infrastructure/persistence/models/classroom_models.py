"""SQLAlchemy models for classroom domain."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Index
)

from app.database.connection import Base


class ClassroomSessionModel(Base):
    """
    SQLAlchemy model for classroom sessions.

    Links tutoring sessions to video rooms.
    """

    __tablename__ = "classroom_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Reference to the booking session
    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One classroom per session
        index=True
    )

    # Participants (denormalized for quick access)
    instructor_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)

    # Video room info
    room_id = Column(String(255), nullable=True)  # Provider-specific room ID (required for 100ms SDK)
    room_name = Column(String(255), nullable=False, unique=True, index=True)
    room_url = Column(String(500), nullable=False)
    provider = Column(String(50), nullable=False)  # "hundredms", "daily", "twilio", etc.

    # Status
    status = Column(String(20), nullable=False, default="created")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_classroom_instructor_status', 'instructor_id', 'status'),
        Index('idx_classroom_student_status', 'student_id', 'status'),
        Index('idx_classroom_status', 'status'),
    )
