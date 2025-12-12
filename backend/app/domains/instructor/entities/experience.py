"""Experience entity."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Experience:
    """
    Work experience entity.

    Represents work experience of instructor.
    """

    # Identity
    id: Optional[int] = None
    instructor_id: int = None

    # Experience Details
    company_name: str = ""
    position: str = ""
    start_date: str = ""  # Format: "YYYY-MM"
    end_date: Optional[str] = None  # Format: "YYYY-MM" or "Present"
    description: Optional[str] = None
    is_current: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        instructor_id: int,
        company_name: str,
        position: str,
        start_date: str,
        end_date: Optional[str] = None,
        description: Optional[str] = None,
        is_current: bool = False,
    ) -> "Experience":
        """
        Create experience entry.

        Args:
            instructor_id: Instructor ID
            company_name: Company name
            position: Position/role
            start_date: Start date (YYYY-MM)
            end_date: Optional end date (YYYY-MM or "Present")
            description: Optional description
            is_current: Whether this is current position

        Returns:
            Experience instance

        Raises:
            ValueError: If validation fails
        """
        # Validate
        if not company_name or not company_name.strip():
            raise ValueError("Company name is required")
        if not position or not position.strip():
            raise ValueError("Position is required")
        if not start_date or not cls._validate_date_format(start_date):
            raise ValueError("Invalid start date format (use YYYY-MM)")

        if end_date and end_date.lower() != "present":
            if not cls._validate_date_format(end_date):
                raise ValueError("Invalid end date format (use YYYY-MM or 'Present')")

        # If current, end_date should be "Present" or None
        if is_current and end_date and end_date.lower() != "present":
            raise ValueError("Current position should have 'Present' as end date")

        return cls(
            instructor_id=instructor_id,
            company_name=company_name.strip(),
            position=position.strip(),
            start_date=start_date,
            end_date=end_date,
            description=description.strip() if description else None,
            is_current=is_current,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @staticmethod
    def _validate_date_format(date_str: str) -> bool:
        """Validate date format YYYY-MM."""
        try:
            parts = date_str.split("-")
            if len(parts) != 2:
                return False
            year, month = int(parts[0]), int(parts[1])
            return 1950 <= year <= 2100 and 1 <= month <= 12
        except:
            return False

    def update(
        self,
        company_name: Optional[str] = None,
        position: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        description: Optional[str] = None,
        is_current: Optional[bool] = None,
    ) -> None:
        """Update experience details."""
        if company_name:
            self.company_name = company_name.strip()
        if position:
            self.position = position.strip()
        if start_date:
            if not self._validate_date_format(start_date):
                raise ValueError("Invalid start date format")
            self.start_date = start_date
        if end_date is not None:
            if end_date.lower() != "present" and not self._validate_date_format(end_date):
                raise ValueError("Invalid end date format")
            self.end_date = end_date
        if description is not None:
            self.description = description.strip() if description else None
        if is_current is not None:
            self.is_current = is_current

        self.updated_at = datetime.utcnow()

    def mark_as_current(self) -> None:
        """Mark position as current."""
        self.is_current = True
        self.end_date = "Present"
        self.updated_at = datetime.utcnow()

    def mark_as_ended(self, end_date: str) -> None:
        """
        Mark position as ended.

        Args:
            end_date: End date (YYYY-MM)
        """
        if not self._validate_date_format(end_date):
            raise ValueError("Invalid end date format")

        self.is_current = False
        self.end_date = end_date
        self.updated_at = datetime.utcnow()

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Experience):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.id) if self.id else hash(id(self))
