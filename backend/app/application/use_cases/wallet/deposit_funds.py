"""Use case for depositing funds into an instructor's wallet."""

from decimal import Decimal
from typing import Optional

from app.domains.wallet.entities import Wallet, WalletTransaction
from app.domains.wallet.repositories import IWalletRepository
from app.domains.wallet.value_objects import Money


class DepositFundsUseCase:
    """
    Use case for depositing funds into instructor wallet.

    Called when a session payment is completed.
    """

    def __init__(self, wallet_repo: IWalletRepository):
        """
        Initialize DepositFundsUseCase.

        Args:
            wallet_repo: Repository for wallet persistence
        """
        self.wallet_repo = wallet_repo

    def execute(
        self,
        instructor_id: int,
        amount: float,
        reference_type: str,
        reference_id: int,
        description: str,
        currency: str = "INR",
    ) -> WalletTransaction:
        """
        Deposit funds into instructor's wallet.

        Args:
            instructor_id: The instructor profile ID
            amount: Amount to deposit
            reference_type: Source type ('session', 'manual', etc.)
            reference_id: ID of source entity (e.g., session ID)
            description: Human-readable description
            currency: Currency code (default INR)

        Returns:
            The created deposit transaction

        Raises:
            ValueError: If wallet not found or deposit fails
        """
        # Get wallet
        wallet = self.wallet_repo.get_by_instructor_id(instructor_id)
        if not wallet:
            raise ValueError(f"Wallet not found for instructor {instructor_id}")

        # Create money value object
        money = Money.create(amount, currency)

        # Perform deposit
        transaction = wallet.deposit(
            amount=money,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
        )

        # Update wallet and save transaction
        self.wallet_repo.update(wallet)
        saved_transaction = self.wallet_repo.save_transaction(transaction)

        return saved_transaction
