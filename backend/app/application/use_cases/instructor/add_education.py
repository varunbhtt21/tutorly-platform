"""Use case for adding education credential to instructor profile."""

from typing import Optional

from app.domains.instructor.entities import Education
from app.domains.instructor.repositories import IEducationRepository


class AddEducationUseCase:
    """
    Use case for adding education credential.

    Allows instructors to add educational credentials (college/university
    degrees) to their profile. Multiple education entries are supported.
    This is part of the background information section (Step 7) of
    onboarding.
    """

    def __init__(self, education_repo: IEducationRepository):
        """
        Initialize AddEducationUseCase.

        Args:
            education_repo: Repository for education entity persistence
        """
        self.education_repo = education_repo

    def execute(
        self,
        instructor_id: int,
        institution_name: str,
        degree: str,
        field_of_study: str,
        year_of_graduation: int,
        certificate_url: Optional[str] = None,
    ) -> Education:
        """
        Execute the use case to add education credential.

        Args:
            instructor_id: Instructor profile ID
            institution_name: Name of educational institution
            degree: Degree name (e.g., "Bachelor of Science")
            field_of_study: Field of study (e.g., "Computer Science")
            year_of_graduation: Year of graduation
            certificate_url: Optional URL to certificate or diploma

        Returns:
            Created Education entity with ID populated

        Raises:
            ValueError: If validation fails
            RepositoryError: If database operation fails
        """
        # Create education entity using factory method (validates inputs)
        education = Education.create(
            instructor_id=instructor_id,
            institution_name=institution_name,
            degree=degree,
            field_of_study=field_of_study,
            year_of_graduation=year_of_graduation,
            certificate_url=certificate_url,
        )

        # Save to repository
        saved_education = self.education_repo.save(education)

        return saved_education
