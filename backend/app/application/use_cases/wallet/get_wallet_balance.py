"""Use case for getting wallet balance and transaction history."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List

from app.domains.wallet.entities import Wallet, WalletTransaction
from app.domains.wallet.repositories import IWalletRepository
from app.domains.wallet.value_objects import TransactionType, TransactionStatus


@dataclass
class WalletBalanceResponse:
    """Response containing wallet balance information."""

    wallet_id: int
    instructor_id: int
    balance: Decimal  # Current withdrawable balance
    total_earned: Decimal  # Lifetime earnings
    total_withdrawn: Decimal  # Lifetime withdrawals
    currency: str
    status: str
    can_withdraw: bool


@dataclass
class TransactionHistoryResponse:
    """Response containing transaction history."""

    transactions: List[WalletTransaction]
    total_count: int
    has_more: bool


class GetWalletBalanceUseCase:
    """
    Use case for getting wallet balance.
    """

    def __init__(self, wallet_repo: IWalletRepository):
        """
        Initialize GetWalletBalanceUseCase.

        Args:
            wallet_repo: Repository for wallet persistence
        """
        self.wallet_repo = wallet_repo

    def execute(self, instructor_id: int) -> WalletBalanceResponse:
        """
        Get wallet balance for an instructor.

        Args:
            instructor_id: The instructor profile ID

        Returns:
            WalletBalanceResponse with balance details

        Raises:
            ValueError: If wallet not found
        """
        wallet = self.wallet_repo.get_by_instructor_id(instructor_id)
        if not wallet:
            raise ValueError(f"Wallet not found for instructor {instructor_id}")

        return WalletBalanceResponse(
            wallet_id=wallet.id,
            instructor_id=wallet.instructor_id,
            balance=wallet.balance,
            total_earned=wallet.total_earned,
            total_withdrawn=wallet.total_withdrawn,
            currency=wallet.currency,
            status=wallet.status.value,
            can_withdraw=wallet.can_withdraw,
        )


class GetTransactionHistoryUseCase:
    """
    Use case for getting transaction history.
    """

    def __init__(self, wallet_repo: IWalletRepository):
        self.wallet_repo = wallet_repo

    def execute(
        self,
        instructor_id: int,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> TransactionHistoryResponse:
        """
        Get transaction history for an instructor.

        Args:
            instructor_id: The instructor profile ID
            transaction_type: Optional filter by type
            status: Optional filter by status
            limit: Max results (default 50)
            offset: Pagination offset (default 0)

        Returns:
            TransactionHistoryResponse with transactions

        Raises:
            ValueError: If wallet not found
        """
        wallet = self.wallet_repo.get_by_instructor_id(instructor_id)
        if not wallet:
            raise ValueError(f"Wallet not found for instructor {instructor_id}")

        # Convert string filters to enums
        txn_type = TransactionType(transaction_type) if transaction_type else None
        txn_status = TransactionStatus(status) if status else None

        # Get transactions
        transactions = self.wallet_repo.get_transactions_by_wallet_id(
            wallet_id=wallet.id,
            transaction_type=txn_type,
            status=txn_status,
            limit=limit + 1,  # Get one extra to check if there are more
            offset=offset,
        )

        # Check if there are more results
        has_more = len(transactions) > limit
        if has_more:
            transactions = transactions[:limit]

        # Get total count
        total_count = self.wallet_repo.count_transactions(
            wallet_id=wallet.id,
            transaction_type=txn_type,
            status=txn_status,
        )

        return TransactionHistoryResponse(
            transactions=transactions,
            total_count=total_count,
            has_more=has_more,
        )
