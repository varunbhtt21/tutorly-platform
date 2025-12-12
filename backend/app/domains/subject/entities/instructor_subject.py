"""InstructorSubject domain entity - join entity for instructor-subject relationship."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class InstructorSubject:
    """
    InstructorSubject join entity.

    Represents the relationship between an instructor and a subject,
    including proficiency level and teaching experience details.
    """

    # Identity
    id: Optional[str] = None

    # Foreign Keys
    instructor_id: str = None
    subject_id: str = None

    # Proficiency Information
    years_of_experience: float = 0.0
    description: Optional[str] = None

    # Primary Subject Indicator
    is_primary: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        instructor_id: str,
        subject_id: str,
        years_of_experience: float = 0.0,
        description: Optional[str] = None,
        is_primary: bool = False,
    ) -> "InstructorSubject":
        """
        Create a new InstructorSubject relationship.

        Args:
            instructor_id: ID of the instructor
            subject_id: ID of the subject
            years_of_experience: Years of experience with this subject
            description: Optional description of expertise
            is_primary: Whether this is the instructor's primary subject

        Returns:
            New InstructorSubject instance

        Raises:
            ValueError: If required fields are invalid or years_of_experience is negative
        """
        if not instructor_id or not instructor_id.strip():
            raise ValueError("Instructor ID is required")

        if not subject_id or not subject_id.strip():
            raise ValueError("Subject ID is required")

        if years_of_experience < 0:
            raise ValueError("Years of experience cannot be negative")

        now = datetime.utcnow()

        return cls(
            instructor_id=instructor_id.strip(),
            subject_id=subject_id.strip(),
            years_of_experience=years_of_experience,
            description=description.strip() if description else None,
            is_primary=is_primary,
            created_at=now,
            updated_at=now,
        )

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def update(
        self,
        years_of_experience: Optional[float] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Update instructor's experience with this subject.

        Args:
            years_of_experience: Updated years of experience
            description: Updated expertise description

        Raises:
            ValueError: If years_of_experience is negative
        """
        if years_of_experience is not None:
            if years_of_experience < 0:
                raise ValueError("Years of experience cannot be negative")
            self.years_of_experience = years_of_experience

        if description is not None:
            self.description = description.strip() if description else None

        self.updated_at = datetime.utcnow()

    def set_as_primary(self) -> None:
        """
        Mark this subject as the instructor's primary subject.

        Primary subjects are highlighted in search results and instructor profiles.
        """
        if self.is_primary:
            raise ValueError("Subject is already marked as primary")

        self.is_primary = True
        self.updated_at = datetime.utcnow()

    def remove_primary(self) -> None:
        """
        Unmark this subject as the instructor's primary subject.

        Note: At least one subject should remain primary (enforced at service layer).
        """
        if not self.is_primary:
            raise ValueError("Subject is not marked as primary")

        self.is_primary = False
        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Domain Properties
    # ========================================================================

    @property
    def is_expert(self) -> bool:
        """Check if instructor is an expert (5+ years of experience)."""
        return self.years_of_experience >= 5.0

    @property
    def is_intermediate(self) -> bool:
        """Check if instructor has intermediate experience (2-5 years)."""
        return 2.0 <= self.years_of_experience < 5.0

    @property
    def is_beginner(self) -> bool:
        """Check if instructor is a beginner (<2 years)."""
        return self.years_of_experience < 2.0

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, InstructorSubject):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.id) if self.id else hash(id(self))
