"""Use case for deleting instructor availability."""

from app.domains.scheduling.repositories import IAvailabilityRepository


class DeleteAvailabilityUseCase:
    """Use case for deleting an availability slot."""

    def __init__(self, availability_repo: IAvailabilityRepository):
        """
        Initialize use case with repository.

        Args:
            availability_repo: Availability repository implementation
        """
        self.availability_repo = availability_repo

    def execute(self, availability_id: int, instructor_id: int) -> bool:
        """
        Execute the use case.

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

        return self.availability_repo.delete(availability_id)
