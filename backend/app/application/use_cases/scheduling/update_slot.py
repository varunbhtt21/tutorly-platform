"""Use case for updating (resizing) an individual booking slot."""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from app.domains.scheduling.repositories import IBookingSlotRepository, IAvailabilityRepository


@dataclass
class UpdateSlotInput:
    """Input data for updating a slot."""
    slot_id: int
    instructor_id: int  # For authorization
    start_at: Optional[str] = None  # ISO datetime string
    end_at: Optional[str] = None    # ISO datetime string


@dataclass
class UpdateSlotOutput:
    """Output data from updating a slot."""
    id: int
    instructor_id: int
    start_at: str
    end_at: str
    duration_minutes: int
    status: str
    availability_rule_id: Optional[int]


class UpdateSlotUseCase:
    """
    Use case for updating an individual booking slot.

    Allows resizing slots by changing start/end times.
    Only works for slots from one-time availability (slots with slot_id).
    Also updates the parent availability rule's time range.
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
            availability_repo: Availability repository implementation (optional)
        """
        self.booking_slot_repo = booking_slot_repo
        self.availability_repo = availability_repo

    def execute(self, input_data: UpdateSlotInput) -> UpdateSlotOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data for updating the slot

        Returns:
            UpdateSlotOutput with updated slot data

        Raises:
            ValueError: If slot not found, unauthorized, or invalid update
        """
        # Get existing slot
        slot = self.booking_slot_repo.get_by_id(input_data.slot_id)

        if not slot:
            raise ValueError(f"Slot with ID {input_data.slot_id} not found")

        # Verify ownership
        if slot.instructor_id != input_data.instructor_id:
            raise ValueError("Unauthorized: slot belongs to another instructor")

        # Check if slot can be modified
        if slot.is_booked:
            raise ValueError("Cannot modify a booked slot")

        # Parse new times
        new_start = slot.start_at
        new_end = slot.end_at

        if input_data.start_at:
            new_start = datetime.fromisoformat(input_data.start_at)

        if input_data.end_at:
            new_end = datetime.fromisoformat(input_data.end_at)

        # Validate times
        if new_start >= new_end:
            raise ValueError("Start time must be before end time")

        # Calculate new duration
        duration_minutes = int((new_end - new_start).total_seconds() / 60)

        if duration_minutes < 15:
            raise ValueError("Slot duration must be at least 15 minutes")

        # Check for overlaps with other slots (excluding this slot)
        if self.booking_slot_repo.has_overlap(
            instructor_id=slot.instructor_id,
            start_at=new_start,
            end_at=new_end,
            exclude_id=slot.id
        ):
            raise ValueError("Updated slot would overlap with another slot")

        # Resize the slot
        slot.resize(new_start, new_end)

        # Save changes
        saved = self.booking_slot_repo.save(slot)

        # Also update the availability rule's time range if we have the repository
        if self.availability_repo and saved.availability_rule_id:
            self._update_availability_time_range(saved.availability_rule_id)

        return UpdateSlotOutput(
            id=saved.id,
            instructor_id=saved.instructor_id,
            start_at=saved.start_at.isoformat(),
            end_at=saved.end_at.isoformat(),
            duration_minutes=saved.duration_minutes,
            status=saved.status.value,
            availability_rule_id=saved.availability_rule_id,
        )

    def _update_availability_time_range(self, availability_id: int) -> None:
        """
        Update availability rule's start/end time to match the min/max of its slots.

        This keeps the sidebar display in sync with actual slot times.
        """
        if not self.availability_repo:
            return

        # Get the availability
        availability = self.availability_repo.get_by_id(availability_id)
        if not availability:
            return

        # Get all slots for this availability
        slots = self.booking_slot_repo.get_by_availability_rule(availability_id)
        if not slots:
            return

        # Find min start and max end times
        min_start = min(s.start_at for s in slots)
        max_end = max(s.end_at for s in slots)

        # Update availability's time range
        availability.start_time = time(min_start.hour, min_start.minute)
        availability.end_time = time(max_end.hour, max_end.minute)

        # Save the updated availability
        self.availability_repo.save(availability)
