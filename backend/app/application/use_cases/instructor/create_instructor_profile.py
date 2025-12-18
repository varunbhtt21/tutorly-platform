"""Use case for creating instructor profile."""

from typing import Optional

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.wallet.entities.wallet import Wallet
from app.domains.wallet.repositories import IWalletRepository


class CreateInstructorProfileUseCase:
    """
    Use case for creating a new instructor profile.

    Creates an instructor profile for a user who is transitioning to become
    an instructor. Initializes the profile in DRAFT status with default
    onboarding state.

    Also creates a wallet for the instructor to receive payments - this ensures
    every instructor has a wallet from the moment their profile is created.
    """

    def __init__(
        self,
        instructor_repo: IInstructorProfileRepository,
        wallet_repo: IWalletRepository,
    ):
        """
        Initialize CreateInstructorProfileUseCase.

        Args:
            instructor_repo: Repository for instructor profile persistence
            wallet_repo: Repository for wallet persistence
        """
        self.instructor_repo = instructor_repo
        self.wallet_repo = wallet_repo

    def execute(self, user_id: int) -> InstructorProfile:
        """
        Execute the use case to create instructor profile.

        Creates both the instructor profile and their wallet in a single
        atomic operation. This ensures every instructor has a wallet ready
        to receive payments from the start.

        Args:
            user_id: User ID who is becoming an instructor

        Returns:
            Created InstructorProfile with ID populated

        Raises:
            ValueError: If user already has an instructor profile
            RepositoryError: If database operation fails
        """
        # Check if profile already exists
        existing_profile = self.instructor_repo.get_by_user_id(user_id)
        if existing_profile:
            raise ValueError(f"Instructor profile already exists for user {user_id}")

        # Create new profile using factory method
        profile = InstructorProfile.create_for_user(user_id)

        # Save profile to repository (this assigns the profile ID)
        saved_profile = self.instructor_repo.save(profile)

        # Create wallet for the instructor using their profile ID
        # This ensures instructor can receive payments from their first booking
        wallet = Wallet.create_for_instructor(saved_profile.id)
        self.wallet_repo.save(wallet)

        return saved_profile
