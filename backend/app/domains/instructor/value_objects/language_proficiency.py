"""Language and LanguageProficiency value objects."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class ProficiencyLevel(str, Enum):
    """Language proficiency levels."""

    NATIVE = "native"
    FLUENT = "fluent"
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BASIC = "basic"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Language:
    """
    Language value object.

    Represents a language with proficiency level.
    """

    name: str
    proficiency: ProficiencyLevel

    def __post_init__(self):
        """Validate language."""
        if not self.name or not self.name.strip():
            raise ValueError("Language name cannot be empty")

        # Normalize name
        object.__setattr__(self, 'name', self.name.strip().title())

        if not isinstance(self.proficiency, ProficiencyLevel):
            raise ValueError("Invalid proficiency level")

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} ({self.proficiency.value})"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, Language):
            return self.name.lower() == other.name.lower() and self.proficiency == other.proficiency
        return False

    def __hash__(self) -> int:
        """Make Language hashable."""
        return hash((self.name.lower(), self.proficiency))


@dataclass(frozen=True)
class LanguageProficiency:
    """
    Collection of languages spoken by instructor.

    Immutable value object.
    """

    languages: tuple[Language, ...]

    def __post_init__(self):
        """Validate languages."""
        if not self.languages:
            raise ValueError("At least one language is required")

        # Check for duplicates
        seen = set()
        for lang in self.languages:
            if lang.name.lower() in seen:
                raise ValueError(f"Duplicate language: {lang.name}")
            seen.add(lang.name.lower())

    @classmethod
    def create(cls, languages: List[Language]) -> "LanguageProficiency":
        """
        Create LanguageProficiency from list.

        Args:
            languages: List of Language objects

        Returns:
            LanguageProficiency instance
        """
        if not languages:
            raise ValueError("At least one language is required")

        return cls(languages=tuple(languages))

    def has_language(self, language_name: str) -> bool:
        """Check if instructor speaks a language."""
        return any(lang.name.lower() == language_name.lower() for lang in self.languages)

    def get_proficiency(self, language_name: str) -> ProficiencyLevel:
        """Get proficiency level for a language."""
        for lang in self.languages:
            if lang.name.lower() == language_name.lower():
                return lang.proficiency
        raise ValueError(f"Language not found: {language_name}")

    def count(self) -> int:
        """Get number of languages."""
        return len(self.languages)

    def __iter__(self):
        """Make iterable."""
        return iter(self.languages)

    def __len__(self) -> int:
        """Get length."""
        return len(self.languages)

    def __str__(self) -> str:
        """String representation."""
        return ", ".join(str(lang) for lang in self.languages)
