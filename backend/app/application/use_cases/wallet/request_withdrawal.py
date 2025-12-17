"""Use case for requesting a withdrawal from instructor's wallet."""

from typing import Optional, Dict, Any

from app.domains.wallet.entities import WalletTransaction
from app.domains.wallet.repositories import IWalletRepository
from app.domains.wallet.value_objects import Money


class RequestWithdrawalUseCase:
    """
    Use case for requesting withdrawal from instructor wallet.

    Creates a pending withdrawal transaction.
    """

    def __init__(self, wallet_repo: IWalletRepository):
        """
        Initialize RequestWithdrawalUseCase.

        Args:
            wallet_repo: Repository for wallet persistence
        """
        self.wallet_repo = wallet_repo

    def execute(
        self,
        instructor_id: int,
        amount: float,
        payment_method: str,
        payment_details: Optional[Dict[str, Any]] = None,
        currency: str = "INR",
    ) -> WalletTransaction:
        """
        Request withdrawal from instructor's wallet.

        Args:
            instructor_id: The instructor profile ID
            amount: Amount to withdraw
            payment_method: Payment method ('payoneer', 'bank_transfer', etc.)
            payment_details: Details for payment processing
            currency: Currency code (default INR)

        Returns:
            The created pending withdrawal transaction

        Raises:
            ValueError: If wallet not found, insufficient funds, or withdrawal fails
        """
        # Get wallet
        wallet = self.wallet_repo.get_by_instructor_id(instructor_id)
        if not wallet:
            raise ValueError(f"Wallet not found for instructor {instructor_id}")

        # Check for existing pending withdrawals
        pending_withdrawals = self.wallet_repo.get_pending_withdrawals(wallet.id)
        if pending_withdrawals:
            raise ValueError(
                "You have a pending withdrawal. Please wait for it to complete."
            )

        # Create money value object
        money = Money.create(amount, currency)

        # Build extra_data
        extra_data = {
            "payment_method": payment_method,
            **(payment_details or {}),
        }

        # Request withdrawal
        description = f"Withdrawal via {payment_method}"
        transaction = wallet.request_withdrawal(
            amount=money,
            description=description,
            extra_data=extra_data,
        )

        # Update wallet and save transaction
        self.wallet_repo.update(wallet)
        saved_transaction = self.wallet_repo.save_transaction(transaction)

        return saved_transaction


class CompleteWithdrawalUseCase:
    """
    Use case for completing a withdrawal (called by payment webhook/admin).
    """

    def __init__(self, wallet_repo: IWalletRepository):
        self.wallet_repo = wallet_repo

    def execute(self, transaction_id: int) -> WalletTransaction:
        """
        Complete a pending withdrawal.

        Args:
            transaction_id: The withdrawal transaction ID

        Returns:
            The completed transaction

        Raises:
            ValueError: If transaction not found or not a pending withdrawal
        """
        # Get transaction
        transaction = self.wallet_repo.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")

        # Get wallet
        wallet = self.wallet_repo.get_by_id(transaction.wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {transaction.wallet_id}")

        # Complete withdrawal
        wallet.complete_withdrawal(transaction)

        # Update both
        self.wallet_repo.update(wallet)
        self.wallet_repo.update_transaction(transaction)

        return transaction


class FailWithdrawalUseCase:
    """
    Use case for failing a withdrawal (called by payment webhook/admin).
    """

    def __init__(self, wallet_repo: IWalletRepository):
        self.wallet_repo = wallet_repo

    def execute(self, transaction_id: int, reason: str) -> WalletTransaction:
        """
        Fail a pending withdrawal and refund to balance.

        Args:
            transaction_id: The withdrawal transaction ID
            reason: Reason for failure

        Returns:
            The failed transaction

        Raises:
            ValueError: If transaction not found or not a pending withdrawal
        """
        # Get transaction
        transaction = self.wallet_repo.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")

        # Get wallet
        wallet = self.wallet_repo.get_by_id(transaction.wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {transaction.wallet_id}")

        # Fail withdrawal (refunds to balance)
        wallet.fail_withdrawal(transaction, reason)

        # Update both
        self.wallet_repo.update(wallet)
        self.wallet_repo.update_transaction(transaction)

        return transaction
