"""SQLAlchemy implementation of Wallet repository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from app.database.models import (
    Wallet as WalletORM,
    WalletTransaction as WalletTransactionORM,
    TransactionType as TransactionTypeORM,
    TransactionStatus as TransactionStatusORM,
)
from app.domains.wallet.entities import Wallet, WalletTransaction
from app.domains.wallet.repositories import IWalletRepository
from app.domains.wallet.value_objects import TransactionType, TransactionStatus
from app.infrastructure.persistence.mappers.wallet_mapper import WalletMapper


class SQLAlchemyWalletRepository(IWalletRepository):
    """SQLAlchemy implementation of IWalletRepository."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = WalletMapper

    # ========================================================================
    # Wallet Operations
    # ========================================================================

    def save(self, wallet: Wallet) -> Wallet:
        """Save a new wallet."""
        orm_wallet = self.mapper.create_orm_instance(wallet)
        self.db.add(orm_wallet)
        self.db.flush()
        wallet.id = orm_wallet.id
        return wallet

    def get_by_id(self, wallet_id: int) -> Optional[Wallet]:
        """Get wallet by ID."""
        orm_wallet = (
            self.db.query(WalletORM)
            .filter(WalletORM.id == wallet_id)
            .first()
        )
        if not orm_wallet:
            return None
        return self.mapper.to_domain(orm_wallet)

    def get_by_instructor_id(self, instructor_id: int) -> Optional[Wallet]:
        """Get wallet by instructor ID."""
        orm_wallet = (
            self.db.query(WalletORM)
            .filter(WalletORM.instructor_id == instructor_id)
            .first()
        )
        if not orm_wallet:
            return None
        return self.mapper.to_domain(orm_wallet)

    def update(self, wallet: Wallet) -> Wallet:
        """Update an existing wallet."""
        orm_wallet = (
            self.db.query(WalletORM)
            .filter(WalletORM.id == wallet.id)
            .first()
        )
        if not orm_wallet:
            raise ValueError(f"Wallet not found: {wallet.id}")

        # Update fields
        update_data = self.mapper.to_persistence(wallet)
        for key, value in update_data.items():
            setattr(orm_wallet, key, value)

        self.db.flush()
        return wallet

    # ========================================================================
    # Transaction Operations
    # ========================================================================

    def save_transaction(self, transaction: WalletTransaction) -> WalletTransaction:
        """Save a new transaction."""
        orm_txn = self.mapper.create_transaction_orm_instance(transaction)
        self.db.add(orm_txn)
        self.db.flush()
        transaction.id = orm_txn.id
        return transaction

    def get_transaction_by_id(
        self, transaction_id: int
    ) -> Optional[WalletTransaction]:
        """Get transaction by ID."""
        orm_txn = (
            self.db.query(WalletTransactionORM)
            .filter(WalletTransactionORM.id == transaction_id)
            .first()
        )
        if not orm_txn:
            return None
        return self.mapper.transaction_to_domain(orm_txn)

    def update_transaction(
        self, transaction: WalletTransaction
    ) -> WalletTransaction:
        """Update an existing transaction."""
        orm_txn = (
            self.db.query(WalletTransactionORM)
            .filter(WalletTransactionORM.id == transaction.id)
            .first()
        )
        if not orm_txn:
            raise ValueError(f"Transaction not found: {transaction.id}")

        # Update fields
        update_data = self.mapper.transaction_to_persistence(transaction)
        for key, value in update_data.items():
            setattr(orm_txn, key, value)

        self.db.flush()
        return transaction

    def get_transactions_by_wallet_id(
        self,
        wallet_id: int,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[WalletTransaction]:
        """Get transactions for a wallet with optional filters."""
        query = (
            self.db.query(WalletTransactionORM)
            .filter(WalletTransactionORM.wallet_id == wallet_id)
        )

        # Apply filters
        if transaction_type:
            query = query.filter(
                WalletTransactionORM.type == TransactionTypeORM(transaction_type.value)
            )
        if status:
            query = query.filter(
                WalletTransactionORM.status == TransactionStatusORM(status.value)
            )

        # Order by most recent first
        query = query.order_by(WalletTransactionORM.created_at.desc())

        # Apply pagination
        query = query.offset(offset).limit(limit)

        orm_txns = query.all()
        return [self.mapper.transaction_to_domain(txn) for txn in orm_txns]

    def get_pending_withdrawals(
        self, wallet_id: int
    ) -> List[WalletTransaction]:
        """Get all pending withdrawal transactions for a wallet."""
        orm_txns = (
            self.db.query(WalletTransactionORM)
            .filter(WalletTransactionORM.wallet_id == wallet_id)
            .filter(WalletTransactionORM.type == TransactionTypeORM.WITHDRAWAL)
            .filter(WalletTransactionORM.status == TransactionStatusORM.PENDING)
            .order_by(WalletTransactionORM.created_at.desc())
            .all()
        )
        return [self.mapper.transaction_to_domain(txn) for txn in orm_txns]

    def count_transactions(
        self,
        wallet_id: int,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
    ) -> int:
        """Count transactions for a wallet with optional filters."""
        query = (
            self.db.query(WalletTransactionORM)
            .filter(WalletTransactionORM.wallet_id == wallet_id)
        )

        # Apply filters
        if transaction_type:
            query = query.filter(
                WalletTransactionORM.type == TransactionTypeORM(transaction_type.value)
            )
        if status:
            query = query.filter(
                WalletTransactionORM.status == TransactionStatusORM(status.value)
            )

        return query.count()
