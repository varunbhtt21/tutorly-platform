"""InstructorSubject repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import InstructorSubject


class IInstructorSubjectRepository(ABC):
    """
    Repository interface for InstructorSubject join entity.

    Defines the contract for persisting and retrieving instructor-subject
    relationships from the underlying data store.
    """

    @abstractmethod
    def save(self, instructor_subject: InstructorSubject) -> InstructorSubject:
        """
        Save a new instructor-subject relationship.

        Args:
            instructor_subject: InstructorSubject instance to save.

        Returns:
            Saved InstructorSubject with ID populated.

        Raises:
            ValueError: If validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, instructor_subject_id: str) -> Optional[InstructorSubject]:
        """
        Retrieve instructor-subject by ID.

        Args:
            instructor_subject_id: Unique identifier.

        Returns:
            InstructorSubject if found, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_instructor(self, instructor_id: str) -> List[InstructorSubject]:
        """
        Retrieve all subjects taught by an instructor.

        Args:
            instructor_id: Unique instructor identifier.

        Returns:
            List of InstructorSubject instances for the instructor.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_subject(self, subject_id: str) -> List[InstructorSubject]:
        """
        Retrieve all instructors teaching a subject.

        Args:
            subject_id: Unique subject identifier.

        Returns:
            List of InstructorSubject instances for the subject.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def get_by_instructor_and_subject(
        self,
        instructor_id: str,
        subject_id: str,
    ) -> Optional[InstructorSubject]:
        """
        Retrieve specific instructor-subject relationship.

        Args:
            instructor_id: Unique instructor identifier.
            subject_id: Unique subject identifier.

        Returns:
            InstructorSubject if exists, None otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def update(self, instructor_subject: InstructorSubject) -> InstructorSubject:
        """
        Update an existing instructor-subject relationship.

        Args:
            instructor_subject: InstructorSubject with updated fields.

        Returns:
            Updated InstructorSubject.

        Raises:
            ValueError: If validation fails.
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def delete(self, instructor_subject_id: str) -> bool:
        """
        Delete an instructor-subject relationship.

        Args:
            instructor_subject_id: Unique identifier.

        Returns:
            True if deleted, False if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass

    @abstractmethod
    def exists(self, instructor_id: str, subject_id: str) -> bool:
        """
        Check if instructor-subject relationship exists.

        Args:
            instructor_id: Unique instructor identifier.
            subject_id: Unique subject identifier.

        Returns:
            True if relationship exists, False otherwise.

        Raises:
            RepositoryError: If database operation fails.
        """
        pass
