"""Use case for creating a new wallet for an instructor."""

from app.domains.wallet.entities import Wallet
from app.domains.wallet.repositories import IWalletRepository


class CreateWalletUseCase:
    """
    Use case for creating a wallet for an instructor.

    Called automatically when instructor is verified.
    """

    def __init__(self, wallet_repo: IWalletRepository):
        """
        Initialize CreateWalletUseCase.

        Args:
            wallet_repo: Repository for wallet persistence
        """
        self.wallet_repo = wallet_repo

    def execute(self, instructor_id: int) -> Wallet:
        """
        Create a new wallet for an instructor.

        Args:
            instructor_id: The instructor profile ID

        Returns:
            Created Wallet

        Raises:
            ValueError: If wallet already exists for instructor
        """
        # Check if wallet already exists
        existing_wallet = self.wallet_repo.get_by_instructor_id(instructor_id)
        if existing_wallet:
            raise ValueError(f"Wallet already exists for instructor {instructor_id}")

        # Create wallet
        wallet = Wallet.create_for_instructor(instructor_id)

        # Save and return
        saved_wallet = self.wallet_repo.save(wallet)
        return saved_wallet
