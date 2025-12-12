"""Education entity."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Education:
    """
    Education credential entity.

    Represents educational background of instructor.
    """

    # Identity
    id: Optional[int] = None
    instructor_id: int = None

    # Education Details
    institution_name: str = ""
    degree: str = ""
    field_of_study: str = ""
    year_of_graduation: int = None

    # Verification
    certificate_url: Optional[str] = None
    is_verified: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        instructor_id: int,
        institution_name: str,
        degree: str,
        field_of_study: str,
        year_of_graduation: int,
        certificate_url: Optional[str] = None,
    ) -> "Education":
        """
        Create education entry.

        Args:
            instructor_id: Instructor ID
            institution_name: Institution name
            degree: Degree name
            field_of_study: Field of study
            year_of_graduation: Year of graduation
            certificate_url: Optional certificate URL

        Returns:
            Education instance

        Raises:
            ValueError: If validation fails
        """
        # Validate
        if not institution_name or not institution_name.strip():
            raise ValueError("Institution name is required")
        if not degree or not degree.strip():
            raise ValueError("Degree is required")
        if not field_of_study or not field_of_study.strip():
            raise ValueError("Field of study is required")
        if year_of_graduation < 1950 or year_of_graduation > datetime.now().year + 10:
            raise ValueError("Invalid graduation year")

        return cls(
            instructor_id=instructor_id,
            institution_name=institution_name.strip(),
            degree=degree.strip(),
            field_of_study=field_of_study.strip(),
            year_of_graduation=year_of_graduation,
            certificate_url=certificate_url,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update(
        self,
        institution_name: Optional[str] = None,
        degree: Optional[str] = None,
        field_of_study: Optional[str] = None,
        year_of_graduation: Optional[int] = None,
        certificate_url: Optional[str] = None,
    ) -> None:
        """Update education details."""
        if institution_name:
            self.institution_name = institution_name.strip()
        if degree:
            self.degree = degree.strip()
        if field_of_study:
            self.field_of_study = field_of_study.strip()
        if year_of_graduation:
            if year_of_graduation < 1950 or year_of_graduation > datetime.now().year + 10:
                raise ValueError("Invalid graduation year")
            self.year_of_graduation = year_of_graduation
        if certificate_url is not None:
            self.certificate_url = certificate_url

        self.updated_at = datetime.utcnow()

    def verify(self) -> None:
        """Mark education as verified."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Education):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.id) if self.id else hash(id(self))
