"""TimeOff repository interface (Port)."""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional

from ..entities import TimeOff


class ITimeOffRepository(ABC):
    """
    Repository interface for TimeOff aggregate.

    Following Hexagonal Architecture, this is a Port that will be
    implemented by an Adapter in the infrastructure layer.
    """

    @abstractmethod
    def save(self, time_off: TimeOff) -> TimeOff:
        """
        Save a time off (create or update).

        Args:
            time_off: The time off to save

        Returns:
            The saved time off with updated ID and timestamps
        """
        pass

    @abstractmethod
    def get_by_id(self, time_off_id: int) -> Optional[TimeOff]:
        """
        Get time off by ID.

        Args:
            time_off_id: The time off ID

        Returns:
            The time off or None if not found
        """
        pass

    @abstractmethod
    def get_by_instructor(self, instructor_id: int) -> List[TimeOff]:
        """
        Get all time offs for an instructor.

        Args:
            instructor_id: The instructor's profile ID

        Returns:
            List of time offs
        """
        pass

    @abstractmethod
    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[TimeOff]:
        """
        Get time offs overlapping a date range.

        Args:
            instructor_id: The instructor's profile ID
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of time offs in that range
        """
        pass

    @abstractmethod
    def get_active_on_date(
        self,
        instructor_id: int,
        target_date: date
    ) -> List[TimeOff]:
        """
        Get time offs active on a specific date.

        Args:
            instructor_id: The instructor's profile ID
            target_date: The date to check

        Returns:
            List of time offs active on that date
        """
        pass

    @abstractmethod
    def has_overlap(
        self,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if there's an overlapping time off.

        Args:
            instructor_id: The instructor's profile ID
            start_at: Start time
            end_at: End time
            exclude_id: Time off ID to exclude from check

        Returns:
            True if overlap exists
        """
        pass

    @abstractmethod
    def delete(self, time_off_id: int) -> bool:
        """
        Delete a time off.

        Args:
            time_off_id: The time off ID

        Returns:
            True if deleted, False if not found
        """
        pass
