"""
Cancel Booking Use Case.

Cancels a pending payment or refunds a completed payment.
"""

from dataclasses import dataclass
from typing import Optional

from app.domains.payment.repositories.payment_repository import IPaymentRepository
from app.domains.payment.services.payment_gateway import IPaymentGateway
from app.domains.payment.value_objects.enums import PaymentStatus
from app.domains.scheduling.repositories.booking_slot_repository import IBookingSlotRepository
from app.domains.scheduling.repositories.session_repository import ISessionRepository


@dataclass
class CancelBookingRequest:
    """Request to cancel a booking."""

    payment_id: int
    user_id: int  # Who is cancelling
    reason: Optional[str] = None


@dataclass
class CancelBookingResponse:
    """Response from cancel booking."""

    success: bool
    message: str = ""
    refund_initiated: bool = False
    refund_amount: Optional[str] = None


class CancelBookingUseCase:
    """
    Use case for cancelling a booking.

    Handles two scenarios:
    1. Pending/Processing payment: Just cancel the payment
    2. Completed payment: Cancel session, release slot, initiate refund
    """

    def __init__(
        self,
        payment_repo: IPaymentRepository,
        slot_repo: IBookingSlotRepository,
        session_repo: ISessionRepository,
        payment_gateway: IPaymentGateway,
    ):
        """
        Initialize use case with dependencies.

        Args:
            payment_repo: Payment repository
            slot_repo: Booking slot repository
            session_repo: Session repository
            payment_gateway: Payment gateway for refunds
        """
        self.payment_repo = payment_repo
        self.slot_repo = slot_repo
        self.session_repo = session_repo
        self.payment_gateway = payment_gateway

    def execute(self, request: CancelBookingRequest) -> CancelBookingResponse:
        """
        Execute the cancel booking use case.

        Args:
            request: Cancellation request

        Returns:
            CancelBookingResponse with cancellation status
        """
        # 1. Get the payment
        payment = self.payment_repo.get_by_id(request.payment_id)
        if not payment:
            return CancelBookingResponse(
                success=False,
                message=f"Payment {request.payment_id} not found",
            )

        # 2. Handle based on payment status
        if payment.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            # Cancel the payment
            payment.cancel()
            self.payment_repo.update(payment)

            return CancelBookingResponse(
                success=True,
                message="Payment cancelled successfully",
            )

        elif payment.status == PaymentStatus.COMPLETED:
            # Need to cancel session and refund
            return self._handle_completed_payment_cancellation(payment, request)

        elif payment.status == PaymentStatus.CANCELLED:
            return CancelBookingResponse(
                success=False,
                message="Payment is already cancelled",
            )

        elif payment.status == PaymentStatus.REFUNDED:
            return CancelBookingResponse(
                success=False,
                message="Payment has already been refunded",
            )

        else:
            return CancelBookingResponse(
                success=False,
                message=f"Cannot cancel payment in {payment.status.value} status",
            )

    def _handle_completed_payment_cancellation(
        self,
        payment,
        request: CancelBookingRequest,
    ) -> CancelBookingResponse:
        """
        Handle cancellation of a completed payment.

        This involves:
        1. Cancelling the session
        2. Releasing the slot
        3. Initiating refund
        4. Updating payment status
        """
        # 1. Cancel the session if exists
        if payment.session_id:
            session = self.session_repo.get_by_id(payment.session_id)
            if session and session.can_be_cancelled:
                session.cancel(
                    cancelled_by=request.user_id,
                    reason=request.reason,
                )
                self.session_repo.save(session)

        # 2. Release the slot
        slot = self.slot_repo.get_by_id(payment.slot_id)
        if slot and slot.is_booked:
            slot.unbook()
            self.slot_repo.save(slot)

        # 3. Initiate refund with gateway
        refund_initiated = False
        refund_amount = None

        if payment.gateway_payment_id:
            try:
                refund_result = self.payment_gateway.refund_payment(
                    payment_id=payment.gateway_payment_id,
                    notes={
                        "reason": request.reason or "User cancellation",
                        "cancelled_by": request.user_id,
                    },
                )

                if refund_result.is_success:
                    refund_initiated = True
                    refund_amount = f"₹{payment.amount:.0f}"

                    # Update payment status
                    payment.refund(refund_result.refund_id)
                    self.payment_repo.update(payment)
                else:
                    # Refund failed - still mark session cancelled but note the error
                    payment.extra_data["refund_error"] = refund_result.error_message
                    self.payment_repo.update(payment)

                    return CancelBookingResponse(
                        success=True,
                        message=f"Session cancelled but refund failed: {refund_result.error_message}",
                        refund_initiated=False,
                    )

            except Exception as e:
                # Log and continue
                print(f"Refund error: {e}")
                return CancelBookingResponse(
                    success=True,
                    message=f"Session cancelled but refund error: {str(e)}",
                    refund_initiated=False,
                )

        return CancelBookingResponse(
            success=True,
            message="Booking cancelled and refund initiated",
            refund_initiated=refund_initiated,
            refund_amount=refund_amount,
        )
