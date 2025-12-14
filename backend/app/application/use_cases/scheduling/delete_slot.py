"""Use case for deleting an individual booking slot."""

from dataclasses import dataclass
from typing import Optional

from app.domains.scheduling.repositories import IBookingSlotRepository, IAvailabilityRepository


@dataclass
class DeleteSlotInput:
    """Input data for deleting a slot."""
    slot_id: int
    instructor_id: int  # For authorization


@dataclass
class DeleteSlotOutput:
    """Output data from deleting a slot."""
    success: bool
    message: str
    availability_deleted: bool = False  # True if parent availability was also deleted


class DeleteSlotUseCase:
    """
    Use case for deleting an individual booking slot.

    Only works for slots from one-time availability (slots with slot_id).
    Cannot delete booked slots.

    If this is the last slot for a one-time availability rule, the availability
    rule is also deleted to prevent orphaned rules.
    """

    def __init__(
        self,
        booking_slot_repo: IBookingSlotRepository,
        availability_repo: Optional[IAvailabilityRepository] = None
    ):
        """
        Initialize use case with repositories.

        Args:
            booking_slot_repo: Booking slot repository implementation
            availability_repo: Availability repository for cleaning up empty rules
        """
        self.booking_slot_repo = booking_slot_repo
        self.availability_repo = availability_repo

    def execute(self, input_data: DeleteSlotInput) -> DeleteSlotOutput:
        """
        Execute the use case.

        Deletes the booking slot. If this was the last slot for a one-time
        availability rule, the rule is also deleted.

        Args:
            input_data: Input data for deleting the slot

        Returns:
            DeleteSlotOutput with deletion result

        Raises:
            ValueError: If slot not found, unauthorized, or cannot be deleted
        """
        # Get existing slot
        slot = self.booking_slot_repo.get_by_id(input_data.slot_id)

        if not slot:
            raise ValueError(f"Slot with ID {input_data.slot_id} not found")

        # Verify ownership
        if slot.instructor_id != input_data.instructor_id:
            raise ValueError("Unauthorized: slot belongs to another instructor")

        # Check if slot can be deleted
        if slot.is_booked:
            raise ValueError("Cannot delete a booked slot")

        # Remember the availability rule ID before deleting the slot
        availability_rule_id = slot.availability_rule_id

        # Delete the slot
        success = self.booking_slot_repo.delete(slot.id)

        availability_deleted = False

        # Check if we need to clean up the parent availability rule
        if success and self.availability_repo and availability_rule_id:
            # Check if there are any remaining slots for this availability
            remaining_slots = self.booking_slot_repo.get_by_availability_rule(availability_rule_id)
            if not remaining_slots:
                # No more slots - delete the availability rule too
                availability = self.availability_repo.get_by_id(availability_rule_id)
                if availability and availability.availability_type.value == "one_time":
                    self.availability_repo.delete(availability_rule_id)
                    availability_deleted = True

        if success:
            message = f"Slot {slot.id} deleted successfully"
            if availability_deleted:
                message += " (availability rule also removed)"
            return DeleteSlotOutput(
                success=True,
                message=message,
                availability_deleted=availability_deleted,
            )
        else:
            return DeleteSlotOutput(
                success=False,
                message=f"Failed to delete slot {slot.id}"
            )
