"""Experience repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Experience


class IExperienceRepository(ABC):
    """
    Repository interface for Experience entity.

    Defines the contract for persisting and retrieving instructor work
    experience records from the underlying data store.
    """

    @abstractmethod
    def save(self, experience: Experience) -> Experience:
        """
        Save a new experience record.

        Args:
            experience: Experience instance to save.

        Returns:
            Saved Experience with ID populated.

        Raises:
            ValueError: If experience validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, experience_id: int) -> Optional[Experience]:
        """
        Retrieve experience record by ID.

        Args:
            experience_id: Unique experience identifier.

        Returns:
            Experience if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_instructor_id(self, instructor_id: int) -> List[Experience]:
        """
        Retrieve all experience records for an instructor.

        Args:
            instructor_id: Unique instructor identifier.

        Returns:
            List of Experience instances for the instructor.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def update(self, experience: Experience) -> Experience:
        """
        Update an existing experience record.

        Args:
            experience: Experience instance with updated fields.

        Returns:
            Updated Experience.

        Raises:
            ValueError: If experience validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def delete(self, experience_id: int) -> bool:
        """
        Delete an experience record.

        Args:
            experience_id: Unique experience identifier.

        Returns:
            True if experience was deleted, False if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass
