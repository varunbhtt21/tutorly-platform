"""Mapper for Wallet domain entities to/from ORM models."""

import json
from decimal import Decimal
from typing import Dict, Any, Optional

from app.database.models import (
    Wallet as WalletORM,
    WalletTransaction as WalletTransactionORM,
    WalletStatus as WalletStatusORM,
    TransactionType as TransactionTypeORM,
    TransactionStatus as TransactionStatusORM,
)
from app.domains.wallet.entities import Wallet, WalletTransaction
from app.domains.wallet.value_objects import (
    WalletStatus,
    TransactionType,
    TransactionStatus,
)


class WalletMapper:
    """Maps between Wallet domain entity and ORM model."""

    # ========================================================================
    # Wallet Mapping
    # ========================================================================

    @staticmethod
    def to_domain(orm_wallet: WalletORM) -> Wallet:
        """
        Convert ORM model to domain entity.

        Args:
            orm_wallet: SQLAlchemy Wallet model

        Returns:
            Wallet domain entity
        """
        return Wallet(
            id=orm_wallet.id,
            instructor_id=orm_wallet.instructor_id,
            balance=Decimal(str(orm_wallet.balance)) if orm_wallet.balance else Decimal("0.00"),
            total_earned=Decimal(str(orm_wallet.total_earned)) if orm_wallet.total_earned else Decimal("0.00"),
            total_withdrawn=Decimal(str(orm_wallet.total_withdrawn)) if orm_wallet.total_withdrawn else Decimal("0.00"),
            currency=orm_wallet.currency,
            status=WalletStatus(orm_wallet.status.value),
            created_at=orm_wallet.created_at,
            updated_at=orm_wallet.updated_at,
        )

    @staticmethod
    def to_persistence(wallet: Wallet) -> Dict[str, Any]:
        """
        Convert domain entity to persistence dict.

        Args:
            wallet: Wallet domain entity

        Returns:
            Dict suitable for ORM model update
        """
        return {
            "instructor_id": wallet.instructor_id,
            "balance": wallet.balance,
            "total_earned": wallet.total_earned,
            "total_withdrawn": wallet.total_withdrawn,
            "currency": wallet.currency,
            "status": WalletStatusORM(wallet.status.value),
            "updated_at": wallet.updated_at,
        }

    @staticmethod
    def create_orm_instance(wallet: Wallet) -> WalletORM:
        """
        Create new ORM instance from domain entity.

        Args:
            wallet: Wallet domain entity

        Returns:
            New WalletORM instance
        """
        return WalletORM(
            instructor_id=wallet.instructor_id,
            balance=wallet.balance,
            total_earned=wallet.total_earned,
            total_withdrawn=wallet.total_withdrawn,
            currency=wallet.currency,
            status=WalletStatusORM(wallet.status.value),
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
        )

    # ========================================================================
    # Transaction Mapping
    # ========================================================================

    @staticmethod
    def transaction_to_domain(orm_txn: WalletTransactionORM) -> WalletTransaction:
        """
        Convert ORM model to domain entity.

        Args:
            orm_txn: SQLAlchemy WalletTransaction model

        Returns:
            WalletTransaction domain entity
        """
        # Parse extra_data from JSON string
        extra_data = {}
        if orm_txn.extra_data:
            try:
                extra_data = json.loads(orm_txn.extra_data)
            except (json.JSONDecodeError, TypeError):
                extra_data = {}

        return WalletTransaction(
            id=orm_txn.id,
            wallet_id=orm_txn.wallet_id,
            type=TransactionType(orm_txn.type.value),
            amount=Decimal(str(orm_txn.amount)) if orm_txn.amount else Decimal("0.00"),
            balance_after=Decimal(str(orm_txn.balance_after)) if orm_txn.balance_after else Decimal("0.00"),
            status=TransactionStatus(orm_txn.status.value),
            reference_type=orm_txn.reference_type,
            reference_id=orm_txn.reference_id,
            description=orm_txn.description,
            extra_data=extra_data,
            failure_reason=orm_txn.failure_reason,
            created_at=orm_txn.created_at,
            completed_at=orm_txn.completed_at,
        )

    @staticmethod
    def transaction_to_persistence(txn: WalletTransaction) -> Dict[str, Any]:
        """
        Convert domain entity to persistence dict.

        Args:
            txn: WalletTransaction domain entity

        Returns:
            Dict suitable for ORM model update
        """
        # Serialize extra_data to JSON string
        extra_data_str = None
        if txn.extra_data:
            extra_data_str = json.dumps(txn.extra_data)

        return {
            "wallet_id": txn.wallet_id,
            "type": TransactionTypeORM(txn.type.value),
            "amount": txn.amount,
            "balance_after": txn.balance_after,
            "status": TransactionStatusORM(txn.status.value),
            "reference_type": txn.reference_type,
            "reference_id": txn.reference_id,
            "description": txn.description,
            "extra_data": extra_data_str,
            "failure_reason": txn.failure_reason,
            "completed_at": txn.completed_at,
        }

    @staticmethod
    def create_transaction_orm_instance(txn: WalletTransaction) -> WalletTransactionORM:
        """
        Create new ORM instance from domain entity.

        Args:
            txn: WalletTransaction domain entity

        Returns:
            New WalletTransactionORM instance
        """
        # Serialize extra_data to JSON string
        extra_data_str = None
        if txn.extra_data:
            extra_data_str = json.dumps(txn.extra_data)

        return WalletTransactionORM(
            wallet_id=txn.wallet_id,
            type=TransactionTypeORM(txn.type.value),
            amount=txn.amount,
            balance_after=txn.balance_after,
            status=TransactionStatusORM(txn.status.value),
            reference_type=txn.reference_type,
            reference_id=txn.reference_id,
            description=txn.description,
            extra_data=extra_data_str,
            failure_reason=txn.failure_reason,
            created_at=txn.created_at,
            completed_at=txn.completed_at,
        )
