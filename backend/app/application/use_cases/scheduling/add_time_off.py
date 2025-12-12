"""Use case for adding instructor time off."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domains.scheduling.entities import TimeOff
from app.domains.scheduling.repositories import ITimeOffRepository


@dataclass
class AddTimeOffInput:
    """Input data for adding time off."""
    instructor_id: int
    start_at: str  # ISO datetime string
    end_at: str    # ISO datetime string
    reason: Optional[str] = None


@dataclass
class AddTimeOffOutput:
    """Output data from adding time off."""
    id: int
    instructor_id: int
    start_at: str
    end_at: str
    reason: Optional[str]
    duration_hours: float


class AddTimeOffUseCase:
    """Use case for adding instructor time off."""

    def __init__(self, time_off_repo: ITimeOffRepository):
        """
        Initialize use case with repository.

        Args:
            time_off_repo: Time off repository implementation
        """
        self.time_off_repo = time_off_repo

    def execute(self, input_data: AddTimeOffInput) -> AddTimeOffOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data for adding time off

        Returns:
            AddTimeOffOutput with created time off

        Raises:
            ValueError: If validation fails or overlap detected
        """
        # Parse datetime values
        start_at = datetime.fromisoformat(input_data.start_at.replace('Z', '+00:00'))
        end_at = datetime.fromisoformat(input_data.end_at.replace('Z', '+00:00'))

        # Validate times
        if start_at >= end_at:
            raise ValueError("Start time must be before end time")

        # Check for overlap with existing time off
        if self.time_off_repo.has_overlap(
            instructor_id=input_data.instructor_id,
            start_at=start_at,
            end_at=end_at,
        ):
            raise ValueError("Overlapping time off already exists")

        # Create time off entity
        time_off = TimeOff.create_single(
            instructor_id=input_data.instructor_id,
            start_at=start_at,
            end_at=end_at,
            reason=input_data.reason,
        )

        # Save to repository
        saved = self.time_off_repo.save(time_off)

        return AddTimeOffOutput(
            id=saved.id,
            instructor_id=saved.instructor_id,
            start_at=saved.start_at.isoformat(),
            end_at=saved.end_at.isoformat(),
            reason=saved.reason,
            duration_hours=saved.duration_hours,
        )
