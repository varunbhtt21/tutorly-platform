"""Wallet aggregate root entity."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from app.domains.wallet.value_objects import (
    Money,
    WalletStatus,
    TransactionType,
)
from app.domains.wallet.entities.wallet_transaction import WalletTransaction


@dataclass
class Wallet:
    """
    Wallet aggregate root for instructor earnings.

    Manages balance, tracks lifetime earnings, and creates
    transactions for all wallet operations.
    """

    # Identity
    id: Optional[int] = None
    instructor_id: int = 0

    # Balances
    balance: Decimal = Decimal("0.00")  # Current withdrawable balance
    total_earned: Decimal = Decimal("0.00")  # Lifetime earnings (never decreases)
    total_withdrawn: Decimal = Decimal("0.00")  # Lifetime withdrawals

    # Settings
    currency: str = "INR"
    status: WalletStatus = WalletStatus.ACTIVE

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Domain events (transient)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create_for_instructor(cls, instructor_id: int) -> "Wallet":
        """
        Create a new wallet for an instructor.

        Args:
            instructor_id: The instructor profile ID

        Returns:
            New Wallet instance
        """
        from app.domains.wallet.events import WalletCreated

        wallet = cls(
            instructor_id=instructor_id,
            balance=Decimal("0.00"),
            total_earned=Decimal("0.00"),
            total_withdrawn=Decimal("0.00"),
            currency="INR",
            status=WalletStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        wallet._add_domain_event(
            WalletCreated(
                instructor_id=instructor_id,
                created_at=wallet.created_at,
            )
        )

        return wallet

    # ========================================================================
    # Business Methods - Deposits
    # ========================================================================

    def deposit(
        self,
        amount: Money,
        reference_type: str,
        reference_id: int,
        description: str,
    ) -> WalletTransaction:
        """
        Add funds to wallet (e.g., from session payment).

        Args:
            amount: Amount to deposit
            reference_type: Source type ('session', 'manual', etc.)
            reference_id: ID of source entity
            description: Human-readable description

        Returns:
            The created transaction

        Raises:
            ValueError: If wallet cannot receive deposits or amount is invalid
        """
        from app.domains.wallet.events import FundsDeposited

        # Validate
        if not self.status.can_receive_deposits:
            raise ValueError(f"Wallet cannot receive deposits in status: {self.status}")
        if not amount.is_positive():
            raise ValueError("Deposit amount must be positive")
        if amount.currency != self.currency:
            raise ValueError(
                f"Currency mismatch: wallet is {self.currency}, got {amount.currency}"
            )

        # Update balances
        self.balance += amount.amount
        self.total_earned += amount.amount
        self.updated_at = datetime.utcnow()

        # Create transaction
        transaction = WalletTransaction.create_deposit(
            wallet_id=self.id,
            amount=amount,
            balance_after=Money.create(self.balance, self.currency),
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
        )

        # Emit event
        self._add_domain_event(
            FundsDeposited(
                wallet_id=self.id,
                instructor_id=self.instructor_id,
                amount=amount.as_float,
                new_balance=float(self.balance),
                reference_type=reference_type,
                reference_id=reference_id,
                deposited_at=datetime.utcnow(),
            )
        )

        return transaction

    # ========================================================================
    # Business Methods - Withdrawals
    # ========================================================================

    def request_withdrawal(
        self,
        amount: Money,
        description: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> WalletTransaction:
        """
        Request withdrawal of funds.

        Creates a pending withdrawal transaction and deducts from balance.
        The actual transfer happens externally (payment provider).

        Args:
            amount: Amount to withdraw
            description: Human-readable description
            extra_data: Payment method info, destination account, etc.

        Returns:
            The created pending withdrawal transaction

        Raises:
            ValueError: If withdrawal not allowed or insufficient funds
        """
        from app.domains.wallet.events import WithdrawalRequested

        # Validate
        if not self.status.can_withdraw:
            raise ValueError(f"Withdrawals not allowed in status: {self.status}")
        if not amount.is_positive():
            raise ValueError("Withdrawal amount must be positive")
        if amount.currency != self.currency:
            raise ValueError(
                f"Currency mismatch: wallet is {self.currency}, got {amount.currency}"
            )
        if amount.amount > self.balance:
            raise ValueError(
                f"Insufficient funds: balance is ${self.balance:.2f}, "
                f"requested ${amount.amount:.2f}"
            )

        # Deduct from balance immediately (held for withdrawal)
        self.balance -= amount.amount
        self.updated_at = datetime.utcnow()

        # Create pending withdrawal transaction
        transaction = WalletTransaction.create_withdrawal(
            wallet_id=self.id,
            amount=amount,
            balance_after=Money.create(self.balance, self.currency),
            description=description,
            extra_data=extra_data,
        )

        # Emit event
        self._add_domain_event(
            WithdrawalRequested(
                wallet_id=self.id,
                instructor_id=self.instructor_id,
                amount=amount.as_float,
                new_balance=float(self.balance),
                requested_at=datetime.utcnow(),
            )
        )

        return transaction

    def complete_withdrawal(self, transaction: WalletTransaction) -> None:
        """
        Mark a withdrawal as completed.

        Called after payment provider confirms transfer.

        Args:
            transaction: The withdrawal transaction to complete

        Raises:
            ValueError: If transaction is not a pending withdrawal
        """
        from app.domains.wallet.events import WithdrawalCompleted

        if transaction.type != TransactionType.WITHDRAWAL:
            raise ValueError("Can only complete withdrawal transactions")
        if not transaction.is_pending:
            raise ValueError("Transaction is not pending")

        # Complete transaction
        transaction.complete()

        # Update lifetime withdrawn
        self.total_withdrawn += transaction.amount
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            WithdrawalCompleted(
                wallet_id=self.id,
                instructor_id=self.instructor_id,
                transaction_id=transaction.id,
                amount=float(transaction.amount),
                completed_at=datetime.utcnow(),
            )
        )

    def fail_withdrawal(self, transaction: WalletTransaction, reason: str) -> None:
        """
        Mark a withdrawal as failed and refund to balance.

        Called when payment provider rejects transfer.

        Args:
            transaction: The withdrawal transaction that failed
            reason: Reason for failure

        Raises:
            ValueError: If transaction is not a pending withdrawal
        """
        from app.domains.wallet.events import WithdrawalFailed

        if transaction.type != TransactionType.WITHDRAWAL:
            raise ValueError("Can only fail withdrawal transactions")
        if not transaction.is_pending:
            raise ValueError("Transaction is not pending")

        # Fail transaction
        transaction.fail(reason)

        # Refund to balance
        self.balance += transaction.amount
        self.updated_at = datetime.utcnow()

        # Emit event
        self._add_domain_event(
            WithdrawalFailed(
                wallet_id=self.id,
                instructor_id=self.instructor_id,
                transaction_id=transaction.id,
                amount=float(transaction.amount),
                reason=reason,
                failed_at=datetime.utcnow(),
            )
        )

    # ========================================================================
    # Business Methods - Refunds
    # ========================================================================

    def process_refund(
        self,
        amount: Money,
        session_id: int,
        description: str,
    ) -> WalletTransaction:
        """
        Process a refund (deduct from wallet).

        Called when a session is refunded to student.

        Args:
            amount: Amount to refund
            session_id: The session being refunded
            description: Human-readable description

        Returns:
            The created refund transaction

        Raises:
            ValueError: If insufficient funds for refund
        """
        if not amount.is_positive():
            raise ValueError("Refund amount must be positive")
        if amount.amount > self.balance:
            raise ValueError(
                f"Insufficient funds for refund: balance is ${self.balance:.2f}, "
                f"refund is ${amount.amount:.2f}"
            )

        # Deduct from balance
        self.balance -= amount.amount
        self.updated_at = datetime.utcnow()

        # Create refund transaction
        transaction = WalletTransaction.create_refund(
            wallet_id=self.id,
            amount=amount,
            balance_after=Money.create(self.balance, self.currency),
            session_id=session_id,
            description=description,
        )

        return transaction

    # ========================================================================
    # Business Methods - Status Management
    # ========================================================================

    def freeze(self) -> None:
        """Freeze wallet (prevent withdrawals)."""
        if self.status == WalletStatus.FROZEN:
            return
        self.status = WalletStatus.FROZEN
        self.updated_at = datetime.utcnow()

    def unfreeze(self) -> None:
        """Unfreeze wallet (allow withdrawals again)."""
        if self.status != WalletStatus.FROZEN:
            raise ValueError(f"Can only unfreeze frozen wallets, got: {self.status}")
        self.status = WalletStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        """Suspend wallet (policy violation)."""
        self.status = WalletStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def balance_money(self) -> Money:
        """Get balance as Money value object."""
        return Money.create(self.balance, self.currency)

    @property
    def total_earned_money(self) -> Money:
        """Get total earned as Money value object."""
        return Money.create(self.total_earned, self.currency)

    @property
    def total_withdrawn_money(self) -> Money:
        """Get total withdrawn as Money value object."""
        return Money.create(self.total_withdrawn, self.currency)

    @property
    def is_active(self) -> bool:
        """Check if wallet is in active status."""
        return self.status == WalletStatus.ACTIVE

    @property
    def can_withdraw(self) -> bool:
        """Check if withdrawals are allowed."""
        return self.status.can_withdraw and self.balance > 0

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
            f"Wallet(id={self.id}, instructor={self.instructor_id}, "
            f"balance=${self.balance:.2f}, earned=${self.total_earned:.2f})"
        )
