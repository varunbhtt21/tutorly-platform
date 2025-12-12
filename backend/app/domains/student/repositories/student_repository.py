"""Student profile repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import StudentProfile


class IStudentProfileRepository(ABC):
    """
    Repository interface for StudentProfile aggregate root.

    Defines the contract for persisting and retrieving student profiles
    from the underlying data store.
    """

    @abstractmethod
    def save(self, profile: StudentProfile) -> StudentProfile:
        """
        Save a new student profile.

        Args:
            profile: StudentProfile instance to save.

        Returns:
            Saved StudentProfile with ID populated.

        Raises:
            ValueError: If profile validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, student_id: int) -> Optional[StudentProfile]:
        """
        Retrieve student profile by ID.

        Args:
            student_id: Unique student identifier.

        Returns:
            StudentProfile if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        """
        Retrieve student profile by user ID.

        Args:
            user_id: Unique user identifier.

        Returns:
            StudentProfile if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[StudentProfile]:
        """
        Retrieve all student profiles.

        Args:
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            List of StudentProfile instances.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def update(self, profile: StudentProfile) -> StudentProfile:
        """
        Update an existing student profile.

        Args:
            profile: StudentProfile instance with updated fields.

        Returns:
            Updated StudentProfile.

        Raises:
            ValueError: If profile validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def delete(self, student_id: int) -> bool:
        """
        Delete a student profile.

        Args:
            student_id: Unique student identifier.

        Returns:
            True if profile was deleted, False if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Count total student profiles.

        Returns:
            Total count of student profiles.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass
