"""
End Classroom Use Case.

Ends a classroom session and cleans up resources.
"""

from dataclasses import dataclass
import logging

from app.domains.classroom.services import IVideoProvider
from app.domains.classroom.repositories import IClassroomRepository
from app.domains.classroom.value_objects import RoomStatus

logger = logging.getLogger(__name__)


@dataclass
class EndClassroomRequest:
    """Request to end a classroom."""
    session_id: int
    user_id: int


class EndClassroomUseCase:
    """
    Use case for ending a video classroom.

    This use case:
    1. Marks the classroom as ended
    2. Optionally deletes the room from provider
    """

    def __init__(
        self,
        classroom_repo: IClassroomRepository,
        video_provider: IVideoProvider,
    ):
        self.classroom_repo = classroom_repo
        self.video_provider = video_provider

    def execute(self, session_id: int, user_id: int) -> bool:
        """
        End a classroom session.

        Args:
            session_id: The tutoring session ID
            user_id: User requesting to end the session

        Returns:
            True if ended successfully

        Raises:
            ValueError: If classroom not found or user not authorized
        """
        # Get classroom
        classroom = self.classroom_repo.get_by_session_id(session_id)
        if not classroom:
            raise ValueError(f"Classroom not found for session {session_id}")

        # Verify user can end (must be participant)
        if not classroom.can_join(user_id):
            raise ValueError("User not authorized to end this classroom")

        # Only instructors can end the session
        if not classroom.is_instructor(user_id):
            raise ValueError("Only instructors can end the session")

        # Mark as ended
        classroom.mark_ended()
        self.classroom_repo.save(classroom)

        # Delete room from provider (cleanup)
        try:
            self.video_provider.delete_room(classroom.room_name)
            logger.info(f"Deleted video room {classroom.room_name}")
        except Exception as e:
            # Log but don't fail - room will expire anyway
            logger.warning(f"Failed to delete room {classroom.room_name}: {e}")

        logger.info(
            f"Ended classroom {classroom.room_name} "
            f"(duration: {classroom.duration_minutes} minutes)"
        )

        return True
