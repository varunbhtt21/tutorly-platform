"""Use case for deleting instructor availability."""

from typing import Optional

from app.domains.scheduling.repositories import IAvailabilityRepository, IBookingSlotRepository


class DeleteAvailabilityUseCase:
    """
    Use case for deleting an availability slot.

    When deleting an availability rule, also deletes all associated booking slots
    to maintain data consistency and prevent orphaned slots.
    """

    def __init__(
        self,
        availability_repo: IAvailabilityRepository,
        booking_slot_repo: Optional[IBookingSlotRepository] = None
    ):
        """
        Initialize use case with repositories.

        Args:
            availability_repo: Availability repository implementation
            booking_slot_repo: Booking slot repository for cleaning up associated slots
        """
        self.availability_repo = availability_repo
        self.booking_slot_repo = booking_slot_repo

    def execute(self, availability_id: int, instructor_id: int) -> bool:
        """
        Execute the use case.

        Deletes the availability rule and all associated booking slots that are
        not already booked. Booked slots are preserved to maintain session integrity.

        Args:
            availability_id: ID of the availability to delete
            instructor_id: ID of the instructor (for authorization)

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If availability doesn't belong to instructor
        """
        # Verify ownership
        availability = self.availability_repo.get_by_id(availability_id)
        if not availability:
            return False

        if availability.instructor_id != instructor_id:
            raise ValueError("Availability does not belong to this instructor")

        # Delete associated booking slots (only non-booked ones)
        if self.booking_slot_repo:
            slots = self.booking_slot_repo.get_by_availability_rule(availability_id)
            for slot in slots:
                # Only delete available or blocked slots, preserve booked ones
                if not slot.is_booked:
                    self.booking_slot_repo.delete(slot.id)

        # Delete the availability rule
        return self.availability_repo.delete(availability_id)
