"""
Join Classroom Use Case.

Generates a meeting token for a user to join a classroom.

This use case is intentionally thin - it delegates complex logic to:
- ClassroomService: Room lifecycle management (create-on-join, room recreation)
- IVideoProvider: Meeting token generation

Following Clean Architecture, the use case orchestrates but doesn't contain
business logic that belongs in domain services.
"""

from dataclasses import dataclass
from datetime import datetime
import logging

from app.domains.classroom.services import (
    IVideoProvider,
    ParticipantRole,
    ClassroomService,
)
from app.domains.classroom.repositories import IClassroomRepository
from app.domains.classroom.value_objects import RoomStatus
from app.domains.user.repositories import IUserRepository

logger = logging.getLogger(__name__)


@dataclass
class JoinClassroomRequest:
    """Request to join a classroom."""
    session_id: int
    user_id: int


@dataclass
class JoinClassroomResponse:
    """Response with meeting token and room details."""
    room_url: str
    token: str
    room_name: str
    participant_name: str
    participant_role: str
    expires_at: datetime
    provider: str


class JoinClassroomUseCase:
    """
    Use case for joining a video classroom.

    This use case orchestrates:
    1. Getting/creating a valid classroom (delegated to ClassroomService)
    2. Verifying user authorization
    3. Generating a meeting token
    4. Updating classroom status

    Complex logic like room lifecycle management (create-on-join, expired room
    recreation) is handled by the ClassroomService domain service.
    """

    def __init__(
        self,
        classroom_service: ClassroomService,
        classroom_repo: IClassroomRepository,
        user_repo: IUserRepository,
        video_provider: IVideoProvider,
    ):
        """
        Initialize the use case.

        Args:
            classroom_service: Domain service for room lifecycle management
            classroom_repo: Repository for classroom persistence
            user_repo: Repository for user data
            video_provider: Adapter for meeting token generation
        """
        self.classroom_service = classroom_service
        self.classroom_repo = classroom_repo
        self.user_repo = user_repo
        self.video_provider = video_provider

    def execute(self, request: JoinClassroomRequest) -> JoinClassroomResponse:
        """
        Generate a meeting token for joining a classroom.

        The ClassroomService handles:
        - Creating classroom if it doesn't exist (create-on-join)
        - Recreating expired video rooms transparently
        - User authorization

        This use case handles:
        - Token generation
        - Classroom status updates
        - Response formatting

        Args:
            request: Contains session_id and user_id

        Returns:
            JoinClassroomResponse with token and room details

        Raises:
            ValueError: If session not found or user not authorized
            TokenCreationError: If token generation fails
            RoomCreationError: If room creation fails
        """
        # Get or create classroom with valid video room
        # ClassroomService handles authorization and room lifecycle
        classroom = self.classroom_service.get_or_create_classroom(
            session_id=request.session_id,
            user_id=request.user_id,
        )

        # Verify classroom is joinable
        if not classroom.is_joinable:
            raise ValueError(f"Classroom is not joinable (status: {classroom.status.value})")

        # Get user for display name
        user = self.user_repo.get_by_id(request.user_id)
        if not user:
            raise ValueError("User not found")

        participant_name = f"{user.first_name} {user.last_name}"

        # Determine role
        if classroom.is_instructor(request.user_id):
            role = ParticipantRole.INSTRUCTOR
        else:
            role = ParticipantRole.STUDENT

        # Generate meeting token
        token_info = self.video_provider.create_meeting_token(
            room_name=classroom.room_name,
            participant_id=request.user_id,
            participant_name=participant_name,
            participant_role=role,
            expires_in_minutes=180,  # 3 hours validity
        )

        # Mark classroom as active if this is first join
        if classroom.status == RoomStatus.CREATED:
            classroom.mark_active()
            self.classroom_repo.save(classroom)
            logger.info(f"Classroom {classroom.room_name} marked as active")

        logger.info(
            f"Generated join token for {participant_name} ({role.value}) "
            f"in classroom {classroom.room_name}"
        )

        return JoinClassroomResponse(
            room_url=token_info.room_url,
            token=token_info.token,
            room_name=classroom.room_name,
            participant_name=participant_name,
            participant_role=role.value,
            expires_at=token_info.expires_at,
            provider=classroom.provider,
        )
