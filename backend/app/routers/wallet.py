"""Wallet API router for instructor earnings management."""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.dependencies import (
    get_current_user,
    get_wallet_repository,
    get_instructor_repository,
)
from app.domains.user.entities import User
from app.domains.wallet.repositories import IWalletRepository
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.application.use_cases.wallet import (
    CreateWalletUseCase,
    DepositFundsUseCase,
    RequestWithdrawalUseCase,
    GetWalletBalanceUseCase,
)
from app.application.use_cases.wallet.get_wallet_balance import (
    GetTransactionHistoryUseCase,
)
from app.application.use_cases.wallet.request_withdrawal import (
    CompleteWithdrawalUseCase,
    FailWithdrawalUseCase,
)

router = APIRouter(prefix="/wallet", tags=["wallet"])


# ============================================================================
# Request/Response Models
# ============================================================================

class WalletBalanceResponse(BaseModel):
    """Response containing wallet balance information."""

    wallet_id: int
    instructor_id: int
    balance: float = Field(description="Current withdrawable balance")
    total_earned: float = Field(description="Lifetime total earnings")
    total_withdrawn: float = Field(description="Lifetime total withdrawals")
    currency: str = "INR"
    status: str
    can_withdraw: bool

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Response for a single transaction."""

    id: int
    type: str
    amount: float
    balance_after: float
    status: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    description: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Response containing list of transactions."""

    transactions: List[TransactionResponse]
    total_count: int
    has_more: bool


class WithdrawalRequest(BaseModel):
    """Request to withdraw funds."""

    amount: float = Field(gt=0, description="Amount to withdraw")
    payment_method: str = Field(description="Payment method (payoneer, bank_transfer, upi)")
    payment_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Payment method specific details"
    )


class WithdrawalResponse(BaseModel):
    """Response after requesting withdrawal."""

    transaction_id: int
    amount: float
    status: str
    payment_method: str
    message: str


# ============================================================================
# Helper function to get instructor profile ID
# ============================================================================

async def get_instructor_profile_id(
    current_user: User,
    instructor_repo: IInstructorProfileRepository,
) -> int:
    """
    Get the instructor profile ID for the current user.

    Raises HTTPException if user is not an instructor or profile not found.
    """
    # Verify user is instructor
    if current_user.role.value != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors have wallets"
        )

    # Get instructor profile
    profile = instructor_repo.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor profile not found"
        )

    return profile.id


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/balance", response_model=WalletBalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    wallet_repo: IWalletRepository = Depends(get_wallet_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
):
    """
    Get current wallet balance for the authenticated instructor.

    Returns balance, total earnings, and withdrawal status.
    """
    instructor_id = await get_instructor_profile_id(current_user, instructor_repo)

    try:
        use_case = GetWalletBalanceUseCase(wallet_repo)
        result = use_case.execute(instructor_id)

        return WalletBalanceResponse(
            wallet_id=result.wallet_id,
            instructor_id=result.instructor_id,
            balance=float(result.balance),
            total_earned=float(result.total_earned),
            total_withdrawn=float(result.total_withdrawn),
            currency=result.currency,
            status=result.status,
            can_withdraw=result.can_withdraw,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    transaction_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    wallet_repo: IWalletRepository = Depends(get_wallet_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
):
    """
    Get transaction history for the authenticated instructor.

    Supports filtering by type and status, with pagination.
    """
    instructor_id = await get_instructor_profile_id(current_user, instructor_repo)

    try:
        use_case = GetTransactionHistoryUseCase(wallet_repo)
        result = use_case.execute(
            instructor_id=instructor_id,
            transaction_type=transaction_type,
            status=status_filter,
            limit=limit,
            offset=offset,
        )

        transactions = [
            TransactionResponse(
                id=txn.id,
                type=txn.type.value,
                amount=float(txn.amount),
                balance_after=float(txn.balance_after),
                status=txn.status.value,
                reference_type=txn.reference_type,
                reference_id=txn.reference_id,
                description=txn.description,
                failure_reason=txn.failure_reason,
                created_at=txn.created_at,
                completed_at=txn.completed_at,
            )
            for txn in result.transactions
        ]

        return TransactionListResponse(
            transactions=transactions,
            total_count=result.total_count,
            has_more=result.has_more,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/withdraw", response_model=WithdrawalResponse)
async def request_withdrawal(
    request: WithdrawalRequest,
    current_user: User = Depends(get_current_user),
    wallet_repo: IWalletRepository = Depends(get_wallet_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
):
    """
    Request a withdrawal from the wallet.

    Creates a pending withdrawal transaction. The actual transfer
    will be processed by the payment system.
    """
    instructor_id = await get_instructor_profile_id(current_user, instructor_repo)

    # Validate payment method
    valid_methods = ["payoneer", "bank_transfer", "upi"]
    if request.payment_method not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
        )

    try:
        use_case = RequestWithdrawalUseCase(wallet_repo)
        transaction = use_case.execute(
            instructor_id=instructor_id,
            amount=request.amount,
            payment_method=request.payment_method,
            payment_details=request.payment_details,
        )

        return WithdrawalResponse(
            transaction_id=transaction.id,
            amount=float(transaction.amount),
            status=transaction.status.value,
            payment_method=request.payment_method,
            message="Withdrawal request submitted. You will be notified once processed.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/withdraw/{transaction_id}", response_model=TransactionResponse)
async def get_withdrawal_status(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    wallet_repo: IWalletRepository = Depends(get_wallet_repository),
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository),
):
    """
    Get status of a specific withdrawal transaction.
    """
    instructor_id = await get_instructor_profile_id(current_user, instructor_repo)

    transaction = wallet_repo.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Verify transaction belongs to user's wallet
    wallet = wallet_repo.get_by_instructor_id(instructor_id)
    if not wallet or transaction.wallet_id != wallet.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction does not belong to your wallet"
        )

    return TransactionResponse(
        id=transaction.id,
        type=transaction.type.value,
        amount=float(transaction.amount),
        balance_after=float(transaction.balance_after),
        status=transaction.status.value,
        reference_type=transaction.reference_type,
        reference_id=transaction.reference_id,
        description=transaction.description,
        failure_reason=transaction.failure_reason,
        created_at=transaction.created_at,
        completed_at=transaction.completed_at,
    )
