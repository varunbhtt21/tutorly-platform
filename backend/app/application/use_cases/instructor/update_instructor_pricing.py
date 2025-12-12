"""Use case for updating instructor pricing."""

from typing import Optional

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.instructor.value_objects import Pricing


class UpdateInstructorPricingUseCase:
    """
    Use case for updating instructor pricing.

    Updates the instructor's session pricing including regular session price
    and optional trial session price. This is typically Step 6 of the
    onboarding process.
    """

    def __init__(self, instructor_repo: IInstructorProfileRepository):
        """
        Initialize UpdateInstructorPricingUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
        """
        self.instructor_repo = instructor_repo

    def execute(
        self,
        instructor_id: int,
        regular_price: float,
        trial_price: Optional[float] = None,
    ) -> InstructorProfile:
        """
        Execute the use case to update instructor pricing.

        Args:
            instructor_id: Instructor profile ID
            regular_price: Price for 50-minute regular session
            trial_price: Optional price for 25-minute trial session

        Returns:
            Updated InstructorProfile

        Raises:
            ValueError: If profile not found or pricing validation fails
            RepositoryError: If database operation fails
        """
        # Get profile
        profile = self.instructor_repo.get_by_id(instructor_id)
        if not profile:
            raise ValueError(f"Instructor profile not found: {instructor_id}")

        # Create Pricing value object (validates constraints)
        pricing = Pricing.create(regular_price, trial_price)

        # Update profile using domain logic
        profile.update_pricing(pricing)

        # Save updated profile
        updated_profile = self.instructor_repo.update(profile)

        return updated_profile
