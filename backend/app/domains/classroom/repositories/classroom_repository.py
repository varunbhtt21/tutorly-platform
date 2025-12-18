"""
Classroom Repository Interface.

Defines the contract for classroom session persistence.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.domains.classroom.entities import ClassroomSession
from app.domains.classroom.value_objects import RoomStatus


class IClassroomRepository(ABC):
    """
    Interface for Classroom Session persistence.

    Implementations handle storage of classroom session records
    that link tutoring sessions to video rooms.
    """

    @abstractmethod
    def save(self, classroom: ClassroomSession) -> ClassroomSession:
        """
        Save a classroom session (create or update).

        Args:
            classroom: The classroom session to save

        Returns:
            The saved classroom session with ID populated
        """
        pass

    @abstractmethod
    def get_by_id(self, classroom_id: int) -> Optional[ClassroomSession]:
        """
        Get a classroom session by its ID.

        Args:
            classroom_id: The classroom session ID

        Returns:
            The classroom session or None if not found
        """
        pass

    @abstractmethod
    def get_by_session_id(self, session_id: int) -> Optional[ClassroomSession]:
        """
        Get a classroom session by the tutoring session ID.

        Args:
            session_id: The tutoring session ID (from booking)

        Returns:
            The classroom session or None if not found
        """
        pass

    @abstractmethod
    def get_by_room_name(self, room_name: str) -> Optional[ClassroomSession]:
        """
        Get a classroom session by room name.

        Args:
            room_name: The video provider room name

        Returns:
            The classroom session or None if not found
        """
        pass

    @abstractmethod
    def get_active_for_user(self, user_id: int) -> List[ClassroomSession]:
        """
        Get all active classroom sessions for a user.

        Args:
            user_id: The user's ID (can be instructor or student)

        Returns:
            List of active classroom sessions
        """
        pass

    @abstractmethod
    def update_status(self, classroom_id: int, status: RoomStatus) -> bool:
        """
        Update the status of a classroom session.

        Args:
            classroom_id: The classroom session ID
            status: The new status

        Returns:
            True if updated, False if not found
        """
        pass

    @abstractmethod
    def delete(self, classroom_id: int) -> bool:
        """
        Delete a classroom session record.

        Args:
            classroom_id: The classroom session ID

        Returns:
            True if deleted, False if not found
        """
        pass
