"""Password value object with strength validation."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Password:
    """
    Password value object.

    Ensures password meets strength requirements.
    Stores hashed version - never stores plain text.
    """

    hashed_value: str

    # Password strength requirements
    MIN_LENGTH = 8
    MAX_LENGTH = 128

    # Password pattern: at least one uppercase, lowercase, digit, special char
    STRENGTH_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_+=\-\[\]{}|\\:;"\'<>,.~/`])'
    )

    @classmethod
    def create_from_plain(cls, plain_password: str, hasher_func) -> "Password":
        """
        Create Password from plain text.

        Args:
            plain_password: Plain text password
            hasher_func: Function to hash password (dependency injection)

        Returns:
            Password value object with hashed value

        Raises:
            ValueError: If password doesn't meet strength requirements
        """
        # Validate strength
        if not plain_password:
            raise ValueError("Password cannot be empty")

        if len(plain_password) < cls.MIN_LENGTH:
            raise ValueError(f"Password must be at least {cls.MIN_LENGTH} characters")

        if len(plain_password) > cls.MAX_LENGTH:
            raise ValueError(f"Password must not exceed {cls.MAX_LENGTH} characters")

        if not cls.STRENGTH_PATTERN.search(plain_password):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )

        # Hash the password
        hashed = hasher_func(plain_password)

        return cls(hashed_value=hashed)

    @classmethod
    def create_from_hash(cls, hashed_password: str) -> "Password":
        """
        Create Password from already hashed value.

        Used when loading from database.

        Args:
            hashed_password: Already hashed password

        Returns:
            Password value object
        """
        if not hashed_password:
            raise ValueError("Hashed password cannot be empty")

        return cls(hashed_value=hashed_password)

    def verify(self, plain_password: str, verifier_func) -> bool:
        """
        Verify plain password against hashed value.

        Args:
            plain_password: Plain text password to verify
            verifier_func: Function to verify password (dependency injection)

        Returns:
            True if password matches, False otherwise
        """
        return verifier_func(plain_password, self.hashed_value)

    def __str__(self) -> str:
        """String representation (masked for security)."""
        return "********"

    def __repr__(self) -> str:
        """Representation (masked for security)."""
        return "Password(hashed_value='********')"

    def __eq__(self, other) -> bool:
        """Password equality comparison."""
        if isinstance(other, Password):
            return self.hashed_value == other.hashed_value
        return False

    def __hash__(self) -> int:
        """Make Password hashable."""
        return hash(self.hashed_value)
