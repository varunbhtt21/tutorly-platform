"""Wallet repository interface (Port)."""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.domains.wallet.entities import Wallet, WalletTransaction
from app.domains.wallet.value_objects import TransactionType, TransactionStatus


class IWalletRepository(ABC):
    """
    Repository interface for Wallet aggregate.

    This is the Port in Ports & Adapters pattern.
    Implementation lives in infrastructure layer.
    """

    # ========================================================================
    # Wallet Operations
    # ========================================================================

    @abstractmethod
    def save(self, wallet: Wallet) -> Wallet:
        """
        Save a new wallet.

        Args:
            wallet: Wallet to save

        Returns:
            Saved wallet with ID
        """
        pass

    @abstractmethod
    def get_by_id(self, wallet_id: int) -> Optional[Wallet]:
        """
        Get wallet by ID.

        Args:
            wallet_id: Wallet ID

        Returns:
            Wallet if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_instructor_id(self, instructor_id: int) -> Optional[Wallet]:
        """
        Get wallet by instructor ID.

        Args:
            instructor_id: Instructor profile ID

        Returns:
            Wallet if found, None otherwise
        """
        pass

    @abstractmethod
    def update(self, wallet: Wallet) -> Wallet:
        """
        Update an existing wallet.

        Args:
            wallet: Wallet with updated fields

        Returns:
            Updated wallet
        """
        pass

    # ========================================================================
    # Transaction Operations
    # ========================================================================

    @abstractmethod
    def save_transaction(self, transaction: WalletTransaction) -> WalletTransaction:
        """
        Save a new transaction.

        Args:
            transaction: Transaction to save

        Returns:
            Saved transaction with ID
        """
        pass

    @abstractmethod
    def get_transaction_by_id(
        self, transaction_id: int
    ) -> Optional[WalletTransaction]:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction if found, None otherwise
        """
        pass

    @abstractmethod
    def update_transaction(
        self, transaction: WalletTransaction
    ) -> WalletTransaction:
        """
        Update an existing transaction.

        Args:
            transaction: Transaction with updated fields

        Returns:
            Updated transaction
        """
        pass

    @abstractmethod
    def get_transactions_by_wallet_id(
        self,
        wallet_id: int,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[WalletTransaction]:
        """
        Get transactions for a wallet with optional filters.

        Args:
            wallet_id: Wallet ID
            transaction_type: Optional filter by type
            status: Optional filter by status
            limit: Max results (default 50)
            offset: Pagination offset (default 0)

        Returns:
            List of transactions
        """
        pass

    @abstractmethod
    def get_pending_withdrawals(
        self, wallet_id: int
    ) -> List[WalletTransaction]:
        """
        Get all pending withdrawal transactions for a wallet.

        Args:
            wallet_id: Wallet ID

        Returns:
            List of pending withdrawal transactions
        """
        pass

    @abstractmethod
    def count_transactions(
        self,
        wallet_id: int,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
    ) -> int:
        """
        Count transactions for a wallet with optional filters.

        Args:
            wallet_id: Wallet ID
            transaction_type: Optional filter by type
            status: Optional filter by status

        Returns:
            Transaction count
        """
        pass
