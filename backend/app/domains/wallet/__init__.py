"""Wallet domain module."""

from app.domains.wallet.entities import Wallet, WalletTransaction
from app.domains.wallet.value_objects import (
    Money,
    WalletStatus,
    TransactionType,
    TransactionStatus,
)
from app.domains.wallet.repositories import IWalletRepository
from app.domains.wallet.events import (
    WalletCreated,
    FundsDeposited,
    WithdrawalRequested,
    WithdrawalCompleted,
    WithdrawalFailed,
)

__all__ = [
    # Entities
    "Wallet",
    "WalletTransaction",
    # Value Objects
    "Money",
    "WalletStatus",
    "TransactionType",
    "TransactionStatus",
    # Repositories
    "IWalletRepository",
    # Events
    "WalletCreated",
    "FundsDeposited",
    "WithdrawalRequested",
    "WithdrawalCompleted",
    "WithdrawalFailed",
]
