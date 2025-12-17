"""WalletTransaction entity for tracking all wallet operations."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from app.domains.wallet.value_objects import (
    Money,
    TransactionType,
    TransactionStatus,
)


@dataclass
class WalletTransaction:
    """
    Entity representing a single wallet transaction.

    Tracks deposits, withdrawals, refunds, and adjustments
    with full audit trail including balance snapshots.
    """

    # Identity
    id: Optional[int] = None
    wallet_id: int = 0

    # Transaction details
    type: TransactionType = TransactionType.DEPOSIT
    amount: Decimal = Decimal("0.00")
    balance_after: Decimal = Decimal("0.00")
    status: TransactionStatus = TransactionStatus.PENDING

    # Reference to source (e.g., session, withdrawal request)
    reference_type: Optional[str] = None  # 'session', 'withdrawal', 'refund', 'manual'
    reference_id: Optional[int] = None
    description: Optional[str] = None

    # Additional data (payment provider info, etc.)
    extra_data: Dict[str, Any] = field(default_factory=dict)

    # Failure tracking
    failure_reason: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Domain events (transient)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create_deposit(
        cls,
        wallet_id: int,
        amount: Money,
        balance_after: Money,
        reference_type: str,
        reference_id: int,
        description: str,
    ) -> "WalletTransaction":
        """
        Create a deposit transaction.

        Args:
            wallet_id: ID of the wallet
            amount: Amount being deposited
            balance_after: Wallet balance after this transaction
            reference_type: Type of reference (e.g., 'session')
            reference_id: ID of the reference entity
            description: Human-readable description

        Returns:
            New WalletTransaction for deposit
        """
        return cls(
            wallet_id=wallet_id,
            type=TransactionType.DEPOSIT,
            amount=amount.amount,
            balance_after=balance_after.amount,
            status=TransactionStatus.COMPLETED,  # Deposits complete immediately
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

    @classmethod
    def create_withdrawal(
        cls,
        wallet_id: int,
        amount: Money,
        balance_after: Money,
        description: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> "WalletTransaction":
        """
        Create a withdrawal transaction (starts as pending).

        Args:
            wallet_id: ID of the wallet
            amount: Amount being withdrawn
            balance_after: Wallet balance after this transaction
            description: Human-readable description
            extra_data: Additional info (payment method, destination, etc.)

        Returns:
            New WalletTransaction for withdrawal
        """
        return cls(
            wallet_id=wallet_id,
            type=TransactionType.WITHDRAWAL,
            amount=amount.amount,
            balance_after=balance_after.amount,
            status=TransactionStatus.PENDING,  # Withdrawals start pending
            reference_type="withdrawal",
            description=description,
            extra_data=extra_data or {},
            created_at=datetime.utcnow(),
        )

    @classmethod
    def create_refund(
        cls,
        wallet_id: int,
        amount: Money,
        balance_after: Money,
        session_id: int,
        description: str,
    ) -> "WalletTransaction":
        """
        Create a refund transaction (deducts from wallet).

        Args:
            wallet_id: ID of the wallet
            amount: Amount being refunded
            balance_after: Wallet balance after this transaction
            session_id: ID of the session being refunded
            description: Human-readable description

        Returns:
            New WalletTransaction for refund
        """
        return cls(
            wallet_id=wallet_id,
            type=TransactionType.REFUND,
            amount=amount.amount,
            balance_after=balance_after.amount,
            status=TransactionStatus.COMPLETED,
            reference_type="session",
            reference_id=session_id,
            description=description,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

    # ========================================================================
    # Business Methods
    # ========================================================================

    def complete(self) -> None:
        """
        Mark transaction as completed.

        Raises:
            ValueError: If transaction is already in a final state
        """
        if self.status.is_final:
            raise ValueError(f"Cannot complete transaction in status: {self.status}")

        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self, reason: str) -> None:
        """
        Mark transaction as failed.

        Args:
            reason: Reason for failure

        Raises:
            ValueError: If transaction is already in a final state
        """
        if self.status.is_final:
            raise ValueError(f"Cannot fail transaction in status: {self.status}")

        self.status = TransactionStatus.FAILED
        self.failure_reason = reason
        self.completed_at = datetime.utcnow()

    def cancel(self) -> None:
        """
        Cancel a pending transaction.

        Raises:
            ValueError: If transaction is not pending
        """
        if self.status != TransactionStatus.PENDING:
            raise ValueError(f"Can only cancel pending transactions, got: {self.status}")

        self.status = TransactionStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def is_credit(self) -> bool:
        """Check if this transaction adds money to wallet."""
        return self.type == TransactionType.DEPOSIT

    @property
    def is_debit(self) -> bool:
        """Check if this transaction removes money from wallet."""
        return self.type in (TransactionType.WITHDRAWAL, TransactionType.REFUND)

    @property
    def is_pending(self) -> bool:
        """Check if transaction is still pending."""
        return self.status == TransactionStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if transaction completed successfully."""
        return self.status == TransactionStatus.COMPLETED

    @property
    def amount_money(self) -> Money:
        """Get amount as Money value object."""
        return Money.create(self.amount)

    # ========================================================================
    # Domain Events
    # ========================================================================

    def _add_domain_event(self, event) -> None:
        """Add a domain event."""
        self._domain_events.append(event)

    def get_domain_events(self) -> List:
        """Get all pending domain events."""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Transaction(id={self.id}, type={self.type.value}, "
            f"amount=${self.amount:.2f}, status={self.status.value})"
        )
