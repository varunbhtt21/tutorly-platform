"""
Classroom Session Entity.

Links a tutoring session to its video room.
This entity tracks the video room lifecycle for a session.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from app.domains.classroom.value_objects import RoomStatus


@dataclass
class ClassroomSession:
    """
    Represents a video classroom for a tutoring session.

    This entity links the booking session (from scheduling domain)
    to the video room (from video provider).

    Attributes:
        id: Unique identifier for this classroom record
        session_id: Reference to the tutoring session (from booking)
        instructor_id: The instructor's user ID
        student_id: The student's user ID
        room_name: Provider-specific room identifier
        room_url: Base URL to join the room
        provider: Name of the video provider (e.g., "daily")
        status: Current room status
        created_at: When the room was created
        expires_at: When the room will expire
        started_at: When the first participant joined
        ended_at: When the session ended
    """

    session_id: int
    instructor_id: int
    student_id: int
    room_name: str
    room_url: str
    provider: str
    status: RoomStatus = RoomStatus.CREATED
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    def mark_active(self) -> None:
        """Mark the session as active (participants joined)."""
        self.status = RoomStatus.ACTIVE
        if not self.started_at:
            self.started_at = datetime.utcnow()

    def mark_ended(self) -> None:
        """Mark the session as ended."""
        self.status = RoomStatus.ENDED
        self.ended_at = datetime.utcnow()

    def mark_expired(self) -> None:
        """Mark the session as expired."""
        self.status = RoomStatus.EXPIRED
        self.ended_at = datetime.utcnow()

    def mark_failed(self) -> None:
        """Mark the session as failed."""
        self.status = RoomStatus.FAILED

    def can_join(self, user_id: int) -> bool:
        """
        Check if a user can join this classroom.

        Only the instructor and student of the session can join.
        """
        return user_id in (self.instructor_id, self.student_id)

    def can_user_access(self, user_id: int) -> bool:
        """
        Alias for can_join - check if a user has access to this classroom.
        """
        return self.can_join(user_id)

    def is_instructor(self, user_id: int) -> bool:
        """Check if the user is the instructor."""
        return user_id == self.instructor_id

    def is_student(self, user_id: int) -> bool:
        """Check if the user is the student."""
        return user_id == self.student_id

    @property
    def is_active(self) -> bool:
        """Check if the session is currently active."""
        return self.status == RoomStatus.ACTIVE

    @property
    def is_joinable(self) -> bool:
        """Check if the session can be joined."""
        return self.status in (RoomStatus.CREATED, RoomStatus.ACTIVE)

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate the actual duration of the session in minutes."""
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            return int(delta.total_seconds() / 60)
        return None
