"""Use case for deleting instructor time off."""

from dataclasses import dataclass

from app.domains.scheduling.repositories import ITimeOffRepository


@dataclass
class DeleteTimeOffInput:
    """Input data for deleting time off."""
    time_off_id: int
    instructor_id: int  # For ownership verification


@dataclass
class DeleteTimeOffOutput:
    """Output data from deleting time off."""
    success: bool
    message: str


class DeleteTimeOffUseCase:
    """Use case for deleting instructor time off."""

    def __init__(self, time_off_repo: ITimeOffRepository):
        """
        Initialize use case with repository.

        Args:
            time_off_repo: Time off repository implementation
        """
        self.time_off_repo = time_off_repo

    def execute(self, input_data: DeleteTimeOffInput) -> DeleteTimeOffOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data for deleting time off

        Returns:
            DeleteTimeOffOutput with deletion result

        Raises:
            ValueError: If time off not found or ownership mismatch
        """
        # Find the time off
        time_off = self.time_off_repo.find_by_id(input_data.time_off_id)

        if time_off is None:
            raise ValueError("Time off not found")

        # Verify ownership
        if time_off.instructor_id != input_data.instructor_id:
            raise ValueError("Not authorized to delete this time off")

        # Delete from repository
        self.time_off_repo.delete(input_data.time_off_id)

        return DeleteTimeOffOutput(
            success=True,
            message="Time off deleted successfully"
        )
