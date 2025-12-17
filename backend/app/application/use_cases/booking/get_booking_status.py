"""
Get Booking Status Use Case.

Retrieves the current status of a payment/booking.
"""

from dataclasses import dataclass
from typing import Optional

from app.domains.payment.repositories.payment_repository import IPaymentRepository


@dataclass
class BookingStatusResponse:
    """Response containing booking status details."""

    payment_id: int
    status: str
    slot_id: int
    session_id: Optional[int] = None
    amount: str = ""
    currency: str = "INR"
    gateway_order_id: Optional[str] = None
    lesson_type: str = ""
    created_at: str = ""
    completed_at: Optional[str] = None
    failure_reason: Optional[str] = None


class GetBookingStatusUseCase:
    """
    Use case for getting booking/payment status.

    Returns the current status of a payment, including session details
    if the booking has been confirmed.
    """

    def __init__(self, payment_repo: IPaymentRepository):
        """
        Initialize use case.

        Args:
            payment_repo: Payment repository
        """
        self.payment_repo = payment_repo

    def execute(self, payment_id: int) -> Optional[BookingStatusResponse]:
        """
        Get booking status by payment ID.

        Args:
            payment_id: ID of the payment

        Returns:
            BookingStatusResponse or None if not found
        """
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            return None

        return BookingStatusResponse(
            payment_id=payment.id,
            status=payment.status.value,
            slot_id=payment.slot_id,
            session_id=payment.session_id,
            amount=f"₹{payment.amount:.0f}",
            currency=payment.currency,
            gateway_order_id=payment.gateway_order_id,
            lesson_type=payment.lesson_type.value,
            created_at=payment.created_at.isoformat() if payment.created_at else "",
            completed_at=payment.completed_at.isoformat() if payment.completed_at else None,
            failure_reason=payment.failure_reason,
        )

    def execute_by_order_id(self, order_id: str) -> Optional[BookingStatusResponse]:
        """
        Get booking status by gateway order ID.

        Args:
            order_id: Razorpay order ID

        Returns:
            BookingStatusResponse or None if not found
        """
        payment = self.payment_repo.get_by_gateway_order_id(order_id)
        if not payment:
            return None

        return BookingStatusResponse(
            payment_id=payment.id,
            status=payment.status.value,
            slot_id=payment.slot_id,
            session_id=payment.session_id,
            amount=f"₹{payment.amount:.0f}",
            currency=payment.currency,
            gateway_order_id=payment.gateway_order_id,
            lesson_type=payment.lesson_type.value,
            created_at=payment.created_at.isoformat() if payment.created_at else "",
            completed_at=payment.completed_at.isoformat() if payment.completed_at else None,
            failure_reason=payment.failure_reason,
        )
