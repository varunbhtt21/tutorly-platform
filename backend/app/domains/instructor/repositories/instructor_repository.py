"""Instructor profile repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from ..entities import InstructorProfile
from ..value_objects import InstructorStatus
from app.domains.user.entities import User


class IInstructorProfileRepository(ABC):
    """
    Repository interface for InstructorProfile aggregate root.

    Defines the contract for persisting and retrieving instructor profiles
    from the underlying data store.
    """

    @abstractmethod
    def save(self, profile: InstructorProfile) -> InstructorProfile:
        """
        Save a new instructor profile.

        Args:
            profile: InstructorProfile instance to save.

        Returns:
            Saved InstructorProfile with ID populated.

        Raises:
            ValueError: If profile validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, instructor_id: int) -> Optional[InstructorProfile]:
        """
        Retrieve instructor profile by ID.

        Args:
            instructor_id: Unique instructor identifier.

        Returns:
            InstructorProfile if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[InstructorProfile]:
        """
        Retrieve instructor profile by user ID.

        Args:
            user_id: Unique user identifier.

        Returns:
            InstructorProfile if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_all(
        self,
        status: Optional[InstructorStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InstructorProfile]:
        """
        Retrieve all instructor profiles with optional filtering.

        Args:
            status: Optional filter by InstructorStatus.
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            List of InstructorProfile instances.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def update(self, profile: InstructorProfile) -> InstructorProfile:
        """
        Update an existing instructor profile.

        Args:
            profile: InstructorProfile instance with updated fields.

        Returns:
            Updated InstructorProfile.

        Raises:
            ValueError: If profile validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def delete(self, instructor_id: int) -> bool:
        """
        Delete an instructor profile.

        Args:
            instructor_id: Unique instructor identifier.

        Returns:
            True if profile was deleted, False if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def count(self, status: Optional[InstructorStatus] = None) -> int:
        """
        Count instructor profiles with optional filtering.

        Args:
            status: Optional filter by InstructorStatus.

        Returns:
            Total count of matching profiles.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_dashboard_data(self, user_id: int) -> Optional[Tuple[InstructorProfile, User]]:
        """
        Get instructor profile with associated user data for dashboard.

        Retrieves both the instructor profile and user entity in an optimized
        query for dashboard display purposes.

        Args:
            user_id: Unique user identifier.

        Returns:
            Tuple of (InstructorProfile, User) if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_with_user(self, instructor_id: int) -> Optional[Tuple[InstructorProfile, User]]:
        """
        Get instructor profile with associated user data by profile ID.

        Retrieves both the instructor profile and user entity for use cases
        that need instructor details (name, email) along with profile data.

        Args:
            instructor_id: Unique instructor profile identifier.

        Returns:
            Tuple of (InstructorProfile, User) if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass
