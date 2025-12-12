"""Education repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Education


class IEducationRepository(ABC):
    """
    Repository interface for Education entity.

    Defines the contract for persisting and retrieving instructor education
    credentials from the underlying data store.
    """

    @abstractmethod
    def save(self, education: Education) -> Education:
        """
        Save a new education record.

        Args:
            education: Education instance to save.

        Returns:
            Saved Education with ID populated.

        Raises:
            ValueError: If education validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, education_id: int) -> Optional[Education]:
        """
        Retrieve education record by ID.

        Args:
            education_id: Unique education identifier.

        Returns:
            Education if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_instructor_id(self, instructor_id: int) -> List[Education]:
        """
        Retrieve all education records for an instructor.

        Args:
            instructor_id: Unique instructor identifier.

        Returns:
            List of Education instances for the instructor.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def update(self, education: Education) -> Education:
        """
        Update an existing education record.

        Args:
            education: Education instance with updated fields.

        Returns:
            Updated Education.

        Raises:
            ValueError: If education validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def delete(self, education_id: int) -> bool:
        """
        Delete an education record.

        Args:
            education_id: Unique education identifier.

        Returns:
            True if education was deleted, False if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass
