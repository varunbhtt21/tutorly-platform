"""Use case for updating instructor availability."""

from dataclasses import dataclass
from datetime import time
from typing import Optional

from app.domains.scheduling.repositories import IAvailabilityRepository


@dataclass
class UpdateAvailabilityInput:
    """Input data for updating availability."""
    availability_id: int
    instructor_id: int  # For authorization
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    slot_duration_minutes: Optional[int] = None
    break_minutes: Optional[int] = None


@dataclass
class UpdateAvailabilityOutput:
    """Output data after updating availability."""
    success: bool
    message: str
    availability_id: Optional[int] = None


class UpdateAvailabilityUseCase:
    """
    Use case for updating an existing availability.

    Updates time window and optionally slot configuration in place,
    preserving the availability ID and other properties.
    """

    def __init__(self, availability_repo: IAvailabilityRepository):
        """
        Initialize use case with repository.

        Args:
            availability_repo: Availability repository implementation
        """
        self.availability_repo = availability_repo

    def execute(self, input_data: UpdateAvailabilityInput) -> UpdateAvailabilityOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data with availability ID and new time values

        Returns:
            UpdateAvailabilityOutput with success status and message
        """
        # Get existing availability
        availability = self.availability_repo.get_by_id(input_data.availability_id)

        if not availability:
            return UpdateAvailabilityOutput(
                success=False,
                message="Availability not found"
            )

        # Verify ownership
        if availability.instructor_id != input_data.instructor_id:
            raise ValueError("Availability does not belong to this instructor")

        # Parse time strings
        try:
            start_time = time.fromisoformat(input_data.start_time)
            end_time = time.fromisoformat(input_data.end_time)
        except ValueError:
            return UpdateAvailabilityOutput(
                success=False,
                message="Invalid time format. Use HH:MM format."
            )

        # Check for overlaps (excluding current availability)
        has_overlap = self.availability_repo.has_overlap(
            instructor_id=input_data.instructor_id,
            day_of_week=availability.day_of_week,
            specific_date=availability.specific_date,
            start_time=start_time,
            end_time=end_time,
            exclude_id=availability.id
        )

        if has_overlap:
            return UpdateAvailabilityOutput(
                success=False,
                message="Updated time range overlaps with existing availability"
            )

        # Update the time window
        availability.update_time_window(start_time, end_time)

        # Update slot configuration if provided
        if input_data.slot_duration_minutes is not None or input_data.break_minutes is not None:
            new_duration = input_data.slot_duration_minutes or availability.slot_duration_minutes
            new_break = input_data.break_minutes if input_data.break_minutes is not None else availability.break_minutes
            availability.update_slot_config(new_duration, new_break)

        # Save updated availability
        updated = self.availability_repo.save(availability)

        return UpdateAvailabilityOutput(
            success=True,
            message="Availability updated successfully",
            availability_id=updated.id
        )
