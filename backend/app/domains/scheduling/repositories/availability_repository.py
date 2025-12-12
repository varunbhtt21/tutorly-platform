"""Availability repository interface (Port)."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..entities import Availability
from ..value_objects import DayOfWeek


class IAvailabilityRepository(ABC):
    """
    Repository interface for Availability aggregate.

    Following Hexagonal Architecture, this is a Port that will be
    implemented by an Adapter in the infrastructure layer.
    """

    @abstractmethod
    def save(self, availability: Availability) -> Availability:
        """
        Save an availability (create or update).

        Args:
            availability: The availability to save

        Returns:
            The saved availability with updated ID and timestamps
        """
        pass

    @abstractmethod
    def get_by_id(self, availability_id: int) -> Optional[Availability]:
        """
        Get availability by ID.

        Args:
            availability_id: The availability ID

        Returns:
            The availability or None if not found
        """
        pass

    @abstractmethod
    def get_by_instructor(
        self,
        instructor_id: int,
        active_only: bool = True
    ) -> List[Availability]:
        """
        Get all availabilities for an instructor.

        Args:
            instructor_id: The instructor's profile ID
            active_only: Only return active availabilities

        Returns:
            List of availabilities
        """
        pass

    @abstractmethod
    def get_by_instructor_and_date(
        self,
        instructor_id: int,
        target_date: date
    ) -> List[Availability]:
        """
        Get availabilities valid for a specific date.

        Args:
            instructor_id: The instructor's profile ID
            target_date: The date to check

        Returns:
            List of availabilities valid on that date
        """
        pass

    @abstractmethod
    def get_by_instructor_and_day(
        self,
        instructor_id: int,
        day_of_week: DayOfWeek
    ) -> List[Availability]:
        """
        Get recurring availabilities for a specific day of week.

        Args:
            instructor_id: The instructor's profile ID
            day_of_week: The day of week

        Returns:
            List of recurring availabilities for that day
        """
        pass

    @abstractmethod
    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[Availability]:
        """
        Get all availabilities overlapping a date range.

        Args:
            instructor_id: The instructor's profile ID
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of availabilities in that range
        """
        pass

    @abstractmethod
    def delete(self, availability_id: int) -> bool:
        """
        Delete an availability.

        Args:
            availability_id: The availability ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def deactivate(self, availability_id: int) -> bool:
        """
        Deactivate an availability (soft delete).

        Args:
            availability_id: The availability ID

        Returns:
            True if deactivated, False if not found
        """
        pass

    @abstractmethod
    def has_overlap(
        self,
        instructor_id: int,
        day_of_week: Optional[DayOfWeek],
        specific_date: Optional[date],
        start_time,
        end_time,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if there's an overlapping availability.

        Args:
            instructor_id: The instructor's profile ID
            day_of_week: Day of week (for recurring)
            specific_date: Specific date (for one-time)
            start_time: Start time
            end_time: End time
            exclude_id: Availability ID to exclude from check

        Returns:
            True if overlap exists
        """
        pass
