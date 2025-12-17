"""Domain events for wallet operations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class WalletCreated:
    """Event emitted when a new wallet is created for an instructor."""

    instructor_id: int
    created_at: datetime


@dataclass(frozen=True)
class FundsDeposited:
    """Event emitted when funds are deposited into a wallet."""

    wallet_id: Optional[int]
    instructor_id: int
    amount: float
    new_balance: float
    reference_type: str  # 'session', 'manual', etc.
    reference_id: int
    deposited_at: datetime


@dataclass(frozen=True)
class WithdrawalRequested:
    """Event emitted when an instructor requests a withdrawal."""

    wallet_id: Optional[int]
    instructor_id: int
    amount: float
    new_balance: float
    requested_at: datetime


@dataclass(frozen=True)
class WithdrawalCompleted:
    """Event emitted when a withdrawal is successfully processed."""

    wallet_id: Optional[int]
    instructor_id: int
    transaction_id: Optional[int]
    amount: float
    completed_at: datetime


@dataclass(frozen=True)
class WithdrawalFailed:
    """Event emitted when a withdrawal fails."""

    wallet_id: Optional[int]
    instructor_id: int
    transaction_id: Optional[int]
    amount: float
    reason: str
    failed_at: datetime
