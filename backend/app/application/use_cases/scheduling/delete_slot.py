"""Use case for deleting an individual booking slot."""

from dataclasses import dataclass

from app.domains.scheduling.repositories import IBookingSlotRepository


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


class DeleteSlotUseCase:
    """
    Use case for deleting an individual booking slot.

    Only works for slots from one-time availability (slots with slot_id).
    Cannot delete booked slots.
    """

    def __init__(self, booking_slot_repo: IBookingSlotRepository):
        """
        Initialize use case with repository.

        Args:
            booking_slot_repo: Booking slot repository implementation
        """
        self.booking_slot_repo = booking_slot_repo

    def execute(self, input_data: DeleteSlotInput) -> DeleteSlotOutput:
        """
        Execute the use case.

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

        # Delete the slot
        success = self.booking_slot_repo.delete(slot.id)

        if success:
            return DeleteSlotOutput(
                success=True,
                message=f"Slot {slot.id} deleted successfully"
            )
        else:
            return DeleteSlotOutput(
                success=False,
                message=f"Failed to delete slot {slot.id}"
            )
