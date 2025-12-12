"""Email value object with validation."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Email:
    """
    Email value object.

    Ensures email is valid and normalized.
    Immutable - cannot be changed after creation.
    """

    value: str

    # Email regex pattern (basic validation)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    def __post_init__(self):
        """Validate email on creation."""
        if not self.value:
            raise ValueError("Email cannot be empty")

        # Normalize: lowercase and strip whitespace
        normalized = self.value.lower().strip()

        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, 'value', normalized)

        if not self._is_valid():
            raise ValueError(f"Invalid email format: {self.value}")

    def _is_valid(self) -> bool:
        """Check if email matches valid pattern."""
        return bool(self.EMAIL_PATTERN.match(self.value))

    @property
    def domain(self) -> str:
        """Extract domain from email."""
        return self.value.split('@')[1]

    @property
    def local_part(self) -> str:
        """Extract local part (before @) from email."""
        return self.value.split('@')[0]

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __eq__(self, other) -> bool:
        """Email equality comparison."""
        if isinstance(other, Email):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.lower().strip()
        return False

    def __hash__(self) -> int:
        """Make Email hashable for use in sets/dicts."""
        return hash(self.value)
