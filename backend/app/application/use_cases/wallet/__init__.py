"""Wallet use cases."""

from app.application.use_cases.wallet.create_wallet import CreateWalletUseCase
from app.application.use_cases.wallet.deposit_funds import DepositFundsUseCase
from app.application.use_cases.wallet.request_withdrawal import RequestWithdrawalUseCase
from app.application.use_cases.wallet.get_wallet_balance import GetWalletBalanceUseCase

__all__ = [
    "CreateWalletUseCase",
    "DepositFundsUseCase",
    "RequestWithdrawalUseCase",
    "GetWalletBalanceUseCase",
]
