"""Repository interface for BookingSlot aggregate."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional

from app.domains.scheduling.entities import BookingSlot, SlotStatus


class IBookingSlotRepository(ABC):
    """
    Port (interface) for BookingSlot aggregate - Hexagonal Architecture.

    This defines the contract for persistence operations on booking slots.
    Implementations (adapters) will be in the infrastructure layer.
    """

    @abstractmethod
    def save(self, slot: BookingSlot) -> BookingSlot:
        """
        Save a booking slot (create or update).

        Args:
            slot: BookingSlot to save

        Returns:
            Saved BookingSlot with ID populated
        """
        pass

    @abstractmethod
    def save_many(self, slots: List[BookingSlot]) -> List[BookingSlot]:
        """
        Save multiple booking slots in batch.

        Args:
            slots: List of BookingSlots to save

        Returns:
            List of saved BookingSlots with IDs populated
        """
        pass

    @abstractmethod
    def get_by_id(self, slot_id: int) -> Optional[BookingSlot]:
        """
        Get a booking slot by ID.

        Args:
            slot_id: ID of the slot

        Returns:
            BookingSlot if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_instructor(
        self,
        instructor_id: int,
        status: Optional[SlotStatus] = None,
    ) -> List[BookingSlot]:
        """
        Get all booking slots for an instructor.

        Args:
            instructor_id: ID of the instructor
            status: Optional filter by status

        Returns:
            List of BookingSlots
        """
        pass

    @abstractmethod
    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date,
        status: Optional[SlotStatus] = None,
    ) -> List[BookingSlot]:
        """
        Get booking slots for an instructor within a date range.

        Args:
            instructor_id: ID of the instructor
            start_date: Start of date range
            end_date: End of date range
            status: Optional filter by status

        Returns:
            List of BookingSlots within the range
        """
        pass

    @abstractmethod
    def get_by_availability_rule(
        self,
        availability_rule_id: int,
    ) -> List[BookingSlot]:
        """
        Get all slots created from a specific availability rule.

        Args:
            availability_rule_id: ID of the availability rule

        Returns:
            List of BookingSlots from that rule
        """
        pass

    @abstractmethod
    def delete(self, slot_id: int) -> bool:
        """
        Delete a booking slot.

        Args:
            slot_id: ID of the slot to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def delete_by_availability_rule(self, availability_rule_id: int) -> int:
        """
        Delete all slots from a specific availability rule.

        Args:
            availability_rule_id: ID of the availability rule

        Returns:
            Number of slots deleted
        """
        pass

    @abstractmethod
    def has_overlap(
        self,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Check if there's an overlapping slot.

        Args:
            instructor_id: ID of the instructor
            start_at: Start datetime to check
            end_at: End datetime to check
            exclude_id: Optional slot ID to exclude from check

        Returns:
            True if overlap exists
        """
        pass
