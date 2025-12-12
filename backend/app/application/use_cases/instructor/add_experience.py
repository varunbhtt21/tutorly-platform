"""Use case for adding work experience to instructor profile."""

from typing import Optional

from app.domains.instructor.entities import Experience
from app.domains.instructor.repositories import IExperienceRepository


class AddExperienceUseCase:
    """
    Use case for adding work experience.

    Allows instructors to add work experience entries to their profile.
    Multiple experience entries are supported. This is part of the
    background information section (Step 7) of onboarding.
    """

    def __init__(self, experience_repo: IExperienceRepository):
        """
        Initialize AddExperienceUseCase.

        Args:
            experience_repo: Repository for experience entity persistence
        """
        self.experience_repo = experience_repo

    def execute(
        self,
        instructor_id: int,
        company_name: str,
        position: str,
        start_date: str,
        end_date: Optional[str] = None,
        description: Optional[str] = None,
        is_current: bool = False,
    ) -> Experience:
        """
        Execute the use case to add work experience.

        Args:
            instructor_id: Instructor profile ID
            company_name: Name of company
            position: Job position/title
            start_date: Start date in YYYY-MM format
            end_date: Optional end date in YYYY-MM format or "Present"
            description: Optional description of role and responsibilities
            is_current: Whether this is current position

        Returns:
            Created Experience entity with ID populated

        Raises:
            ValueError: If validation fails
            RepositoryError: If database operation fails
        """
        # Create experience entity using factory method (validates inputs)
        experience = Experience.create(
            instructor_id=instructor_id,
            company_name=company_name,
            position=position,
            start_date=start_date,
            end_date=end_date,
            description=description,
            is_current=is_current,
        )

        # Save to repository
        saved_experience = self.experience_repo.save(experience)

        return saved_experience
