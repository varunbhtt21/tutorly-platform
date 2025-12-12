"""Subject domain entity with business logic."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Subject:
    """
    Subject aggregate root.

    Rich domain entity managing subject information and business logic.
    Subjects are predefined categories that instructors can teach.
    """

    # Identity
    id: Optional[str] = None

    # Core Attributes
    name: str = None
    category: str = None
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Status
    is_active: bool = True

    # Statistics
    total_instructors: int = 0

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        name: str,
        category: str,
        description: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> "Subject":
        """
        Create a new Subject.

        Args:
            name: Subject name (e.g., "Mathematics")
            category: Subject category (e.g., "STEM")
            description: Optional detailed description
            icon_url: Optional icon URL for UI display

        Returns:
            New Subject instance

        Raises:
            ValueError: If required fields are invalid
        """
        if not name or not name.strip():
            raise ValueError("Subject name is required")

        if not category or not category.strip():
            raise ValueError("Subject category is required")

        now = datetime.utcnow()

        return cls(
            name=name.strip(),
            category=category.strip(),
            description=description.strip() if description else None,
            icon_url=icon_url.strip() if icon_url else None,
            is_active=True,
            total_instructors=0,
            created_at=now,
            updated_at=now,
        )

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def activate(self) -> None:
        """
        Activate this subject.

        Makes the subject visible to students for searching and selection.
        """
        if self.is_active:
            raise ValueError("Subject is already active")

        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """
        Deactivate this subject.

        Hides the subject from being selected by new instructors.
        Existing instructor-subject mappings remain intact.
        """
        if not self.is_active:
            raise ValueError("Subject is already inactive")

        self.is_active = False
        self.updated_at = datetime.utcnow()

    def update_details(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> None:
        """
        Update subject details.

        Args:
            name: New subject name
            category: New subject category
            description: New description
            icon_url: New icon URL

        Raises:
            ValueError: If provided fields are invalid
        """
        if name is not None:
            if not name.strip():
                raise ValueError("Subject name cannot be empty")
            self.name = name.strip()

        if category is not None:
            if not category.strip():
                raise ValueError("Subject category cannot be empty")
            self.category = category.strip()

        if description is not None:
            self.description = description.strip() if description else None

        if icon_url is not None:
            self.icon_url = icon_url.strip() if icon_url else None

        self.updated_at = datetime.utcnow()

    def increment_instructor_count(self) -> None:
        """Increment the total instructor count for this subject."""
        self.total_instructors += 1
        self.updated_at = datetime.utcnow()

    def decrement_instructor_count(self) -> None:
        """Decrement the total instructor count for this subject."""
        if self.total_instructors > 0:
            self.total_instructors -= 1
            self.updated_at = datetime.utcnow()

    # ========================================================================
    # Domain Properties
    # ========================================================================

    @property
    def instructor_count(self) -> int:
        """Get the total number of instructors teaching this subject."""
        return self.total_instructors

    @property
    def is_available(self) -> bool:
        """Check if subject is available (active and has instructors)."""
        return self.is_active and self.total_instructors > 0

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Subject):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.id) if self.id else hash(id(self))
