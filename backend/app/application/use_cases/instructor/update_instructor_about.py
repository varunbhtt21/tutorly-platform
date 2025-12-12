"""Use case for updating instructor about information."""

from typing import List, Dict, Optional

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.instructor.value_objects import LanguageProficiency, Language, ProficiencyLevel


class UpdateInstructorAboutUseCase:
    """
    Use case for updating instructor about information.

    Updates the instructor's personal information including country of birth
    and languages spoken. This is typically Step 1 of the onboarding process.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize UpdateInstructorAboutUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(
        self,
        instructor_id: int,
        country_of_birth: str,
        languages: List[Dict[str, str]],
    ) -> InstructorProfile:
        """
        Execute the use case to update instructor about information.

        Args:
            instructor_id: Instructor profile ID
            country_of_birth: Country of birth
            languages: List of language dicts with "language" and "proficiency" keys
                      Example: [{"language": "English", "proficiency": "native"}]

        Returns:
            Updated InstructorProfile

        Raises:
            ValueError: If profile not found or validation fails
            RepositoryError: If database operation fails
        """
        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # Validate languages format and create Language objects
        if not languages:
            raise ValueError("At least one language is required")

        language_objects = []
        for lang_dict in languages:
            if "language" not in lang_dict or "proficiency" not in lang_dict:
                raise ValueError("Each language must have 'language' and 'proficiency' keys")

            language_name = lang_dict["language"].strip()
            proficiency_str = lang_dict["proficiency"].strip().lower()

            # Validate proficiency level
            try:
                proficiency = ProficiencyLevel(proficiency_str)
            except ValueError:
                raise ValueError(
                    f"Invalid proficiency level: {proficiency_str}. "
                    f"Must be one of: {', '.join(p.value for p in ProficiencyLevel)}"
                )

            language_objects.append(Language(name=language_name, proficiency=proficiency))

        # Create LanguageProficiency value object
        languages_proficiency = LanguageProficiency.create(language_objects)

        # Update profile using domain logic
        profile.update_about(country_of_birth, languages_proficiency)

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
