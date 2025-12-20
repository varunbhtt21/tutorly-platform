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

    def _get_room_from_provider(self, room_name: str) -> Optional[RoomInfo]:
        """
        Get room info from video provider if it exists and is not expired.

        Args:
            room_name: The room identifier

        Returns:
            RoomInfo if room exists and is valid, None if expired or not found
        """
        room_info = self.video_provider.get_room(room_name)

        if not room_info:
            logger.info(f"Room {room_name} not found on provider")
            return None

        if room_info.expires_at and room_info.expires_at < datetime.now(timezone.utc):
            logger.info(f"Room {room_name} has expired (exp: {room_info.expires_at})")
            return None

        return room_info

    def _sync_classroom_with_provider(
        self, classroom: ClassroomSession, room_info: RoomInfo
    ) -> tuple[ClassroomSession, bool]:
        """
        Synchronize classroom entity with video provider room info.

        This implements the Self-Healing Data Pattern: when we have access
        to authoritative data from the provider, we ensure our local entity
        has all required fields populated.

        Args:
            classroom: The classroom entity to sync
            room_info: Authoritative room info from provider

        Returns:
            Tuple of (updated classroom, whether changes were made)
        """
        needs_update = False

        # Backfill room_id if missing (for classrooms created before room_id was added)
        if classroom.room_id is None and room_info.room_id:
            classroom.room_id = room_info.room_id
            needs_update = True
            logger.info(f"Backfilled room_id for classroom {classroom.id}")

        # Sync other fields that might have drifted
        if classroom.room_url != room_info.room_url:
            classroom.room_url = room_info.room_url
            needs_update = True

        return classroom, needs_update

    def ensure_valid_room(self, classroom: ClassroomSession) -> ClassroomSession:
        """
        Ensure the classroom has a valid video room with complete data.

        This method maintains two invariants:
        1. "A classroom always has a valid room on the video provider"
        2. "A classroom entity has all required fields populated"

        If the room is valid but the entity is missing data (e.g., room_id
        from before a migration), this method backfills it from the provider.

        If the room is expired or deleted, this method recreates it.

        Args:
            classroom: Existing classroom record

        Returns:
            ClassroomSession with valid room and complete data

        Raises:
            ValueError: If session not found
            RoomCreationError: If recreation fails
        """
        # Check if room exists on provider
        room_info = self._get_room_from_provider(classroom.room_name)

        if room_info:
            # Room is valid - sync any missing data from provider
            logger.debug(f"Room {classroom.room_name} is valid")
            classroom, needs_update = self._sync_classroom_with_provider(
                classroom, room_info
            )
            if needs_update:
                classroom = self.classroom_repo.save(classroom)
            return classroom

        # Room is invalid - recreate it
        logger.info(f"Recreating expired/missing room for classroom {classroom.id}")

        room_info = self._create_room_for_session(classroom.session_id)

        # Update classroom with new room details
        classroom.room_id = room_info.room_id
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
        instructor_profile_id: int | None = None,
        student_profile_id: int | None = None,
    ) -> ClassroomSession:
        """
        Get an existing classroom or create a new one for a session.

        This is the main entry point for the "create-on-join" pattern.
        It ensures:
        1. If no classroom exists, create one with a valid video room
        2. If classroom exists but room is invalid, recreate the room
        3. User must be authorized (instructor or student)

        Authorization is done via profile IDs because sessions store profile IDs
        (instructor_profile.id, student_profile.id), not user IDs. The use case
        layer resolves user_id to profile IDs before calling this service.

        Args:
            session_id: The tutoring session ID
            user_id: ID of user requesting access (for logging)
            instructor_profile_id: User's instructor profile ID (if they have one)
            student_profile_id: User's student profile ID (if they have one)

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

        # Authorization: user's profile ID must match session's instructor or student
        # Sessions store profile IDs (instructor_profile.id, student_profile.id)
        is_session_instructor = instructor_profile_id == session.instructor_id
        is_session_student = student_profile_id == session.student_id

        if not (is_session_instructor or is_session_student):
            logger.warning(
                f"Unauthorized access attempt: user {user_id} "
                f"(instructor_profile={instructor_profile_id}, student_profile={student_profile_id}) "
                f"tried to access session {session_id} "
                f"(instructor={session.instructor_id}, student={session.student_id})"
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
            room_id=room_info.room_id,
            room_name=room_info.room_name,
            room_url=room_info.room_url,
            provider=room_info.provider,
            status=RoomStatus.CREATED,
            expires_at=room_info.expires_at,
        )

        saved = self.classroom_repo.save(classroom)
        logger.info(f"Created classroom {saved.id} for session {session_id}")

        return saved
