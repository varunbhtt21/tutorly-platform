"""
Create Classroom Use Case.

Creates a video room for a tutoring session.
"""

from dataclasses import dataclass
from datetime import datetime
import logging

from app.domains.classroom.services import IVideoProvider, RoomConfig
from app.domains.classroom.repositories import IClassroomRepository
from app.domains.classroom.entities import ClassroomSession
from app.domains.classroom.value_objects import RoomStatus
from app.domains.scheduling.repositories import ISessionRepository

logger = logging.getLogger(__name__)


@dataclass
class CreateClassroomRequest:
    """Request to create a classroom for a session."""
    session_id: int
    user_id: int  # User requesting the classroom creation


class CreateClassroomUseCase:
    """
    Use case for creating a video classroom.

    This use case:
    1. Validates the session exists and user is authorized
    2. Checks if classroom already exists (idempotent)
    3. Creates the video room with the provider
    4. Stores the classroom record
    """

    def __init__(
        self,
        classroom_repo: IClassroomRepository,
        session_repo: ISessionRepository,
        video_provider: IVideoProvider,
    ):
        self.classroom_repo = classroom_repo
        self.session_repo = session_repo
        self.video_provider = video_provider

    def execute(self, request: CreateClassroomRequest) -> ClassroomSession:
        """
        Create a classroom for a session.

        Args:
            request: Contains session_id and requesting user_id

        Returns:
            ClassroomSession entity

        Raises:
            ValueError: If session not found or user not authorized
            VideoProviderError: If room creation fails
        """
        # Check if classroom already exists (idempotent)
        existing = self.classroom_repo.get_by_session_id(request.session_id)
        if existing:
            logger.info(f"Classroom already exists for session {request.session_id}")
            return existing

        # Get the session
        session = self.session_repo.get_by_id(request.session_id)
        if not session:
            raise ValueError(f"Session {request.session_id} not found")

        # Verify user is participant
        # Note: session has instructor_id and student_id
        if request.user_id not in (session.instructor_id, session.student_id):
            raise ValueError("User not authorized for this session")

        # Create room with video provider
        room_config = RoomConfig(
            session_id=session.id,
            instructor_id=session.instructor_id,
            student_id=session.student_id,
            scheduled_start=session.start_at,
            duration_minutes=session.duration_minutes,
        )

        room_info = self.video_provider.create_room(room_config)

        # Create classroom entity
        classroom = ClassroomSession(
            session_id=session.id,
            instructor_id=session.instructor_id,
            student_id=session.student_id,
            room_name=room_info.room_name,
            room_url=room_info.room_url,
            provider=room_info.provider,
            status=RoomStatus.CREATED,
            expires_at=room_info.expires_at,
        )

        # Save to database
        saved_classroom = self.classroom_repo.save(classroom)

        logger.info(
            f"Created classroom {saved_classroom.room_name} "
            f"for session {session.id}"
        )

        return saved_classroom
