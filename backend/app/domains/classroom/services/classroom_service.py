"""
Classroom Domain Service.

This domain service encapsulates complex business logic related to classroom
management that doesn't naturally fit in a single entity. It coordinates
between multiple domain objects (ClassroomSession, VideoProvider) to maintain
domain invariants.

Key Responsibilities:
1. Ensure classroom has a valid video room (room lifecycle management)
2. Handle room expiration and recreation transparently
3. Maintain consistency between DB records and video provider state

Design Principle:
The video provider is the SOURCE OF TRUTH for room existence. Our DB stores
metadata about the room, but if the actual room expires/is deleted on the
provider, we recreate it transparently. This follows the "Eventually Consistent"
pattern for distributed systems.

Usage:
    service = ClassroomService(video_provider, session_repo, classroom_repo)
    classroom = service.get_or_create_valid_classroom(session_id, user_id)
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from app.domains.classroom.entities import ClassroomSession
from app.domains.classroom.value_objects import RoomStatus
from app.domains.classroom.repositories import IClassroomRepository
from app.domains.classroom.services.video_provider import (
    IVideoProvider,
    RoomConfig,
    RoomInfo,
)
from app.domains.scheduling.repositories import ISessionRepository

logger = logging.getLogger(__name__)


class ClassroomService:
    """
    Domain service for classroom lifecycle management.

    This service ensures the invariant that a classroom always has a valid
    video room. It handles:
    - Creating new classrooms with video rooms
    - Detecting and recreating expired rooms
    - Synchronizing DB state with video provider state

    The service follows the Single Responsibility Principle - it only
    manages the relationship between classrooms and their video rooms.
    """

    def __init__(
        self,
        video_provider: IVideoProvider,
        session_repo: ISessionRepository,
        classroom_repo: IClassroomRepository,
    ):
        """
        Initialize the classroom service.

        Args:
            video_provider: Adapter for video room creation (Daily.co, etc.)
            session_repo: Repository for session data
            classroom_repo: Repository for classroom persistence
        """
        self.video_provider = video_provider
        self.session_repo = session_repo
        self.classroom_repo = classroom_repo

    def _create_room_for_session(self, session_id: int) -> RoomInfo:
        """
        Create a video room for a session.

        Args:
            session_id: The tutoring session ID

        Returns:
            RoomInfo with provider room details

        Raises:
            ValueError: If session not found
            RoomCreationError: If video provider fails
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        room_config = RoomConfig(
            session_id=session.id,
            instructor_id=session.instructor_id,
            student_id=session.student_id,
            scheduled_start=session.start_at,
            duration_minutes=session.duration_minutes,
        )

        return self.video_provider.create_room(room_config)

    def _is_room_valid(self, room_name: str) -> bool:
        """
        Check if a room exists and is not expired on the provider.

        Args:
            room_name: The room identifier

        Returns:
            True if room exists and is valid, False otherwise
        """
        room_info = self.video_provider.get_room(room_name)

        if not room_info:
            logger.info(f"Room {room_name} not found on provider")
            return False

        if room_info.expires_at and room_info.expires_at < datetime.now(timezone.utc):
            logger.info(f"Room {room_name} has expired (exp: {room_info.expires_at})")
            return False

        return True

    def ensure_valid_room(self, classroom: ClassroomSession) -> ClassroomSession:
        """
        Ensure the classroom has a valid video room.

        If the underlying video room has expired or been deleted,
        this method recreates it and updates the classroom record.

        This maintains the invariant: "A classroom always has a valid room"

        Args:
            classroom: Existing classroom record

        Returns:
            ClassroomSession with valid room (may be updated)

        Raises:
            ValueError: If session not found
            RoomCreationError: If recreation fails
        """
        if self._is_room_valid(classroom.room_name):
            logger.debug(f"Room {classroom.room_name} is valid")
            return classroom

        # Room is invalid - recreate it
        logger.info(f"Recreating expired/missing room for classroom {classroom.id}")

        room_info = self._create_room_for_session(classroom.session_id)

        # Update classroom with new room details
        classroom.room_name = room_info.room_name
        classroom.room_url = room_info.room_url
        classroom.expires_at = room_info.expires_at
        classroom.provider = room_info.provider
        classroom.status = RoomStatus.CREATED

        saved = self.classroom_repo.save(classroom)
        logger.info(f"Classroom {saved.id} updated with new room: {room_info.room_name}")

        return saved

    def get_or_create_classroom(
        self,
        session_id: int,
        user_id: int,
    ) -> ClassroomSession:
        """
        Get an existing classroom or create a new one for a session.

        This is the main entry point for the "create-on-join" pattern.
        It ensures:
        1. If no classroom exists, create one with a valid video room
        2. If classroom exists but room is invalid, recreate the room
        3. User must be authorized (instructor or student)

        Args:
            session_id: The tutoring session ID
            user_id: ID of user requesting access (for authorization)

        Returns:
            ClassroomSession with a guaranteed valid video room

        Raises:
            ValueError: If session not found or user not authorized
            RoomCreationError: If video room creation fails
        """
        # Get session for authorization check
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Authorization: user must be instructor or student
        if user_id not in (session.instructor_id, session.student_id):
            logger.warning(
                f"Unauthorized access attempt: user {user_id} tried to access "
                f"session {session_id} (instructor={session.instructor_id}, "
                f"student={session.student_id})"
            )
            raise ValueError("User not authorized for this session")

        # Check if classroom exists
        classroom = self.classroom_repo.get_by_session_id(session_id)

        if classroom:
            # Ensure existing classroom has valid room
            logger.debug(f"Found existing classroom for session {session_id}")
            return self.ensure_valid_room(classroom)

        # Create new classroom
        logger.info(f"Creating new classroom for session {session_id}")

        room_info = self._create_room_for_session(session_id)

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

        saved = self.classroom_repo.save(classroom)
        logger.info(f"Created classroom {saved.id} for session {session_id}")

        return saved
