"""
Booking Router.

API endpoints for lesson booking and payment flow.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.domains.user.entities import User
from app.core.dependencies import (
    get_current_user,
    get_current_student,
    get_initiate_booking_use_case,
    get_confirm_booking_use_case,
    get_cancel_booking_use_case,
    get_booking_status_use_case,
    get_payment_gateway,
)
from app.application.use_cases.booking import (
    InitiateBookingUseCase,
    ConfirmBookingUseCase,
    CancelBookingUseCase,
    GetBookingStatusUseCase,
)
from app.application.use_cases.booking.initiate_booking import InitiateBookingRequest
from app.application.use_cases.booking.confirm_booking import ConfirmBookingRequest
from app.application.use_cases.booking.cancel_booking import CancelBookingRequest
from app.domains.payment.services.payment_gateway import IPaymentGateway


router = APIRouter(prefix="/booking", tags=["Booking"])


# ============================================================================
# Request/Response Models
# ============================================================================


class InitiateBookingRequestModel(BaseModel):
    """
    Request model for initiating a booking.

    Supports two modes:
    1. Booking an existing one-time slot: Provide slot_id
    2. Booking from recurring availability: Provide availability_rule_id + start_at + end_at + duration_minutes
    """

    instructor_id: int
    lesson_type: str = "trial"  # "trial" or "regular"

    # Option 1: Existing slot ID (for one-time availability)
    slot_id: Optional[int] = None

    # Option 2: Recurring availability info (for dynamically generated slots)
    availability_rule_id: Optional[int] = None
    start_at: Optional[str] = None  # ISO format datetime
    end_at: Optional[str] = None    # ISO format datetime
    duration_minutes: Optional[int] = None


class InitiateBookingResponseModel(BaseModel):
    """Response model for booking initiation."""

    payment_id: int
    razorpay_order_id: str
    razorpay_key: str
    amount: int  # In paise
    currency: str
    instructor_name: str
    slot_start: str
    slot_end: str
    description: str


class ConfirmBookingRequestModel(BaseModel):
    """Request model for confirming a booking after payment."""

    payment_id: int
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class ConfirmBookingResponseModel(BaseModel):
    """Response model for booking confirmation."""

    success: bool
    session_id: Optional[int] = None
    message: str
    instructor_name: str = ""
    session_start: str = ""
    session_end: str = ""
    amount_paid: str = ""


class CancelBookingRequestModel(BaseModel):
    """Request model for cancelling a booking."""

    payment_id: int
    reason: Optional[str] = None


class CancelBookingResponseModel(BaseModel):
    """Response model for booking cancellation."""

    success: bool
    message: str
    refund_initiated: bool = False
    refund_amount: Optional[str] = None


class BookingStatusResponseModel(BaseModel):
    """Response model for booking status."""

    payment_id: int
    status: str
    slot_id: int
    session_id: Optional[int] = None
    amount: str
    currency: str
    gateway_order_id: Optional[str] = None
    lesson_type: str
    created_at: str
    completed_at: Optional[str] = None
    failure_reason: Optional[str] = None


class RazorpayKeyResponse(BaseModel):
    """Response model for Razorpay public key."""

    key: str
    business_name: str = "Tutorly"


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/initiate",
    response_model=InitiateBookingResponseModel,
    summary="Initiate a lesson booking",
    description="Step 1: Select a slot and create a payment order. Returns Razorpay order details for frontend checkout.",
)
async def initiate_booking(
    request: InitiateBookingRequestModel,
    current_user: User = Depends(get_current_student),
    use_case: InitiateBookingUseCase = Depends(get_initiate_booking_use_case),
):
    """
    Initiate a lesson booking.

    This creates a payment order with Razorpay and returns the order details
    needed for the frontend to display the payment checkout.

    The slot is NOT reserved at this stage - reservation happens when
    payment starts processing.
    """
    try:
        result = use_case.execute(
            InitiateBookingRequest(
                student_id=current_user.id,
                instructor_id=request.instructor_id,
                lesson_type=request.lesson_type,
                slot_id=request.slot_id,
                availability_rule_id=request.availability_rule_id,
                start_at=request.start_at,
                end_at=request.end_at,
                duration_minutes=request.duration_minutes,
            )
        )

        return InitiateBookingResponseModel(
            payment_id=result.payment_id,
            razorpay_order_id=result.razorpay_order_id,
            razorpay_key=result.razorpay_key,
            amount=result.amount,
            currency=result.currency,
            instructor_name=result.instructor_name,
            slot_start=result.slot_start,
            slot_end=result.slot_end,
            description=result.description,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate booking: {str(e)}",
        )


@router.post(
    "/verify",
    response_model=ConfirmBookingResponseModel,
    summary="Verify payment and confirm booking",
    description="Step 2: After Razorpay payment, verify the signature and create the session.",
)
async def verify_booking(
    request: ConfirmBookingRequestModel,
    current_user: User = Depends(get_current_student),
    use_case: ConfirmBookingUseCase = Depends(get_confirm_booking_use_case),
):
    """
    Verify payment and confirm booking.

    This is called after the user completes payment on the Razorpay checkout.
    It verifies the payment signature and creates the session.
    """
    result = use_case.execute(
        ConfirmBookingRequest(
            payment_id=request.payment_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_order_id=request.razorpay_order_id,
            razorpay_signature=request.razorpay_signature,
        )
    )

    return ConfirmBookingResponseModel(
        success=result.success,
        session_id=result.session_id,
        message=result.message,
        instructor_name=result.instructor_name,
        session_start=result.session_start,
        session_end=result.session_end,
        amount_paid=result.amount_paid,
    )


@router.post(
    "/cancel",
    response_model=CancelBookingResponseModel,
    summary="Cancel a booking",
    description="Cancel a pending or confirmed booking. Refund will be processed for completed payments.",
)
async def cancel_booking(
    request: CancelBookingRequestModel,
    current_user: User = Depends(get_current_user),
    use_case: CancelBookingUseCase = Depends(get_cancel_booking_use_case),
):
    """
    Cancel a booking.

    Can be used to cancel:
    - Pending payments (before payment is made)
    - Processing payments (during payment)
    - Completed payments (will trigger refund)
    """
    result = use_case.execute(
        CancelBookingRequest(
            payment_id=request.payment_id,
            user_id=current_user.id,
            reason=request.reason,
        )
    )

    return CancelBookingResponseModel(
        success=result.success,
        message=result.message,
        refund_initiated=result.refund_initiated,
        refund_amount=result.refund_amount,
    )


@router.get(
    "/{payment_id}/status",
    response_model=BookingStatusResponseModel,
    summary="Get booking status",
    description="Get the current status of a payment/booking.",
)
async def get_booking_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    use_case: GetBookingStatusUseCase = Depends(get_booking_status_use_case),
):
    """
    Get the status of a booking/payment.
    """
    result = use_case.execute(payment_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    return BookingStatusResponseModel(
        payment_id=result.payment_id,
        status=result.status,
        slot_id=result.slot_id,
        session_id=result.session_id,
        amount=result.amount,
        currency=result.currency,
        gateway_order_id=result.gateway_order_id,
        lesson_type=result.lesson_type,
        created_at=result.created_at,
        completed_at=result.completed_at,
        failure_reason=result.failure_reason,
    )


@router.get(
    "/razorpay-key",
    response_model=RazorpayKeyResponse,
    summary="Get Razorpay public key",
    description="Get the Razorpay public key for frontend checkout integration.",
)
async def get_razorpay_key(
    payment_gateway: IPaymentGateway = Depends(get_payment_gateway),
):
    """
    Get the Razorpay public key for frontend integration.
    """
    return RazorpayKeyResponse(
        key=payment_gateway.get_public_key(),
        business_name="Tutorly",
    )
