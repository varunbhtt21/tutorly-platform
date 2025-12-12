"""Session repository interface (Port)."""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional

from ..entities import Session
from ..value_objects import SessionStatus


class ISessionRepository(ABC):
    """
    Repository interface for Session aggregate.

    Following Hexagonal Architecture, this is a Port that will be
    implemented by an Adapter in the infrastructure layer.
    """

    @abstractmethod
    def save(self, session: Session) -> Session:
        """
        Save a session (create or update).

        Args:
            session: The session to save

        Returns:
            The saved session with updated ID and timestamps
        """
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: The session ID

        Returns:
            The session or None if not found
        """
        pass

    @abstractmethod
    def get_by_instructor(
        self,
        instructor_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """
        Get sessions for an instructor.

        Args:
            instructor_id: The instructor's profile ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            status: Optional status filter

        Returns:
            List of sessions
        """
        pass

    @abstractmethod
    def get_by_student(
        self,
        student_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """
        Get sessions for a student.

        Args:
            student_id: The student's profile ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            status: Optional status filter

        Returns:
            List of sessions
        """
        pass

    @abstractmethod
    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[Session]:
        """
        Get all sessions for an instructor in a date range.

        Args:
            instructor_id: The instructor's profile ID
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of sessions
        """
        pass

    @abstractmethod
    def get_upcoming_by_instructor(
        self,
        instructor_id: int,
        limit: int = 10
    ) -> List[Session]:
        """
        Get upcoming sessions for an instructor.

        Args:
            instructor_id: The instructor's profile ID
            limit: Maximum number of sessions to return

        Returns:
            List of upcoming sessions ordered by start time
        """
        pass

    @abstractmethod
    def get_upcoming_by_student(
        self,
        student_id: int,
        limit: int = 10
    ) -> List[Session]:
        """
        Get upcoming sessions for a student.

        Args:
            student_id: The student's profile ID
            limit: Maximum number of sessions to return

        Returns:
            List of upcoming sessions ordered by start time
        """
        pass

    @abstractmethod
    def has_conflict(
        self,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_session_id: Optional[int] = None
    ) -> bool:
        """
        Check if there's a conflicting session.

        Args:
            instructor_id: The instructor's profile ID
            start_at: Start time
            end_at: End time
            exclude_session_id: Session ID to exclude

        Returns:
            True if conflict exists
        """
        pass

    @abstractmethod
    def count_by_instructor(
        self,
        instructor_id: int,
        status: Optional[SessionStatus] = None
    ) -> int:
        """
        Count sessions for an instructor.

        Args:
            instructor_id: The instructor's profile ID
            status: Optional status filter

        Returns:
            Number of sessions
        """
        pass

    @abstractmethod
    def get_recurring_series(self, parent_session_id: int) -> List[Session]:
        """
        Get all sessions in a recurring series.

        Args:
            parent_session_id: The parent session ID

        Returns:
            List of sessions in the series
        """
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """
        Delete a session.

        Args:
            session_id: The session ID

        Returns:
            True if deleted, False if not found
        """
        pass
