"""Wallet domain enumerations."""

from enum import Enum


class WalletStatus(str, Enum):
    """Status of an instructor's wallet."""

    ACTIVE = "active"  # Normal operation, can deposit/withdraw
    FROZEN = "frozen"  # Temporarily frozen, no withdrawals allowed
    SUSPENDED = "suspended"  # Suspended due to policy violation

    @property
    def can_withdraw(self) -> bool:
        """Check if withdrawals are allowed in this status."""
        return self == WalletStatus.ACTIVE

    @property
    def can_receive_deposits(self) -> bool:
        """Check if deposits are allowed in this status."""
        return self in (WalletStatus.ACTIVE, WalletStatus.FROZEN)


class TransactionType(str, Enum):
    """Type of wallet transaction."""

    DEPOSIT = "deposit"  # Money added from session payment
    WITHDRAWAL = "withdrawal"  # Money withdrawn to external account
    REFUND = "refund"  # Refund deducted from wallet
    ADJUSTMENT = "adjustment"  # Manual adjustment by admin


class TransactionStatus(str, Enum):
    """Status of a wallet transaction."""

    PENDING = "pending"  # Transaction initiated, awaiting processing
    COMPLETED = "completed"  # Transaction successfully processed
    FAILED = "failed"  # Transaction failed
    CANCELLED = "cancelled"  # Transaction cancelled

    @property
    def is_final(self) -> bool:
        """Check if this is a terminal status."""
        return self in (
            TransactionStatus.COMPLETED,
            TransactionStatus.FAILED,
            TransactionStatus.CANCELLED,
        )
