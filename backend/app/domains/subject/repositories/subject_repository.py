"""Subject repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Subject


class ISubjectRepository(ABC):
    """
    Repository interface for Subject aggregate root.

    Defines the contract for persisting and retrieving subjects
    from the underlying data store.
    """

    @abstractmethod
    def save(self, subject: Subject) -> Subject:
        """
        Save a new subject.

        Args:
            subject: Subject instance to save.

        Returns:
            Saved Subject with ID populated.

        Raises:
            ValueError: If subject validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, subject_id: str) -> Optional[Subject]:
        """
        Retrieve subject by ID.

        Args:
            subject_id: Unique subject identifier.

        Returns:
            Subject if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Subject]:
        """
        Retrieve subject by name.

        Args:
            name: Subject name (case-insensitive).

        Returns:
            Subject if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Subject]:
        """
        Retrieve subjects by category.

        Args:
            category: Subject category to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            List of Subject instances matching the category.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> List[Subject]:
        """
        Retrieve all subjects with optional filtering.

        Args:
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            active_only: If True, only return active subjects.

        Returns:
            List of Subject instances.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def update(self, subject: Subject) -> Subject:
        """
        Update an existing subject.

        Args:
            subject: Subject instance with updated fields.

        Returns:
            Updated Subject.

        Raises:
            ValueError: If subject validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def delete(self, subject_id: str) -> bool:
        """
        Delete a subject.

        Args:
            subject_id: Unique subject identifier.

        Returns:
            True if subject was deleted, False if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def count(self, active_only: bool = False) -> int:
        """
        Count subjects with optional filtering.

        Args:
            active_only: If True, only count active subjects.

        Returns:
            Total count of matching subjects.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass
