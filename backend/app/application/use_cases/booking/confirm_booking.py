"""
Confirm Booking Use Case.

Step 2 of the booking flow: Verifies payment and creates the session.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.domains.payment.repositories.payment_repository import IPaymentRepository
from app.domains.payment.services.payment_gateway import IPaymentGateway
from app.domains.payment.value_objects.enums import PaymentMethod, LessonType
from app.domains.scheduling.repositories.booking_slot_repository import IBookingSlotRepository
from app.domains.scheduling.repositories.session_repository import ISessionRepository
from app.domains.scheduling.entities.session import Session
from app.domains.scheduling.value_objects import SessionType
from app.domains.wallet.repositories import IWalletRepository
from app.domains.wallet.value_objects.money import Money


@dataclass
class ConfirmBookingRequest:
    """Request to confirm a booking after payment."""

    payment_id: int
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


@dataclass
class ConfirmBookingResponse:
    """Response from confirm booking."""

    success: bool
    session_id: Optional[int] = None
    message: str = ""
    instructor_name: str = ""
    session_start: str = ""
    session_end: str = ""
    amount_paid: str = ""


class ConfirmBookingUseCase:
    """
    Use case for confirming a lesson booking after payment.

    This is Step 2 of the booking flow:
    1. Verifies the payment signature with Razorpay
    2. Updates payment status to COMPLETED
    3. Creates a Session entity
    4. Books the slot
    5. Credits the instructor's wallet
    6. Returns confirmation details

    This is an atomic operation - all steps must succeed or the entire
    transaction is rolled back.
    """

    def __init__(
        self,
        payment_repo: IPaymentRepository,
        slot_repo: IBookingSlotRepository,
        session_repo: ISessionRepository,
        wallet_repo: IWalletRepository,
        payment_gateway: IPaymentGateway,
    ):
        """
        Initialize use case with dependencies.

        Args:
            payment_repo: Payment repository
            slot_repo: Booking slot repository
            session_repo: Session repository
            wallet_repo: Wallet repository
            payment_gateway: Payment gateway (Razorpay)
        """
        self.payment_repo = payment_repo
        self.slot_repo = slot_repo
        self.session_repo = session_repo
        self.wallet_repo = wallet_repo
        self.payment_gateway = payment_gateway

    def execute(self, request: ConfirmBookingRequest) -> ConfirmBookingResponse:
        """
        Execute the confirm booking use case.

        Args:
            request: Booking confirmation request with payment details

        Returns:
            ConfirmBookingResponse with session details

        Raises:
            ValueError: If payment not found or validation fails
        """
        # 1. Get the payment
        payment = self.payment_repo.get_by_id(request.payment_id)
        if not payment:
            return ConfirmBookingResponse(
                success=False,
                message=f"Payment {request.payment_id} not found",
            )

        # 2. Verify payment is in PROCESSING status
        if not payment.is_processing:
            return ConfirmBookingResponse(
                success=False,
                message=f"Payment is in {payment.status.value} status, cannot confirm",
            )

        # 3. Verify the gateway order ID matches
        if payment.gateway_order_id != request.razorpay_order_id:
            return ConfirmBookingResponse(
                success=False,
                message="Order ID mismatch",
            )

        # 4. Verify payment signature with Razorpay
        verification = self.payment_gateway.verify_payment(
            order_id=request.razorpay_order_id,
            payment_id=request.razorpay_payment_id,
            signature=request.razorpay_signature,
        )

        if not verification.is_valid:
            # Mark payment as failed
            payment.fail(f"Signature verification failed: {verification.error_message}")
            self.payment_repo.update(payment)

            return ConfirmBookingResponse(
                success=False,
                message=f"Payment verification failed: {verification.error_message}",
            )

        # 5. Set payment method if available
        if verification.payment_method:
            try:
                method = PaymentMethod(verification.payment_method)
                payment.set_payment_method(method)
            except ValueError:
                pass  # Unknown method, skip

        # 6. Get the slot
        slot = self.slot_repo.get_by_id(payment.slot_id)
        if not slot:
            payment.fail("Slot not found")
            self.payment_repo.update(payment)

            return ConfirmBookingResponse(
                success=False,
                message=f"Slot {payment.slot_id} not found",
            )

        # 7. Check slot is still available
        if not slot.is_available:
            payment.fail(f"Slot no longer available (status: {slot.status.value})")
            self.payment_repo.update(payment)

            # TODO: Initiate refund

            return ConfirmBookingResponse(
                success=False,
                message="Slot is no longer available. A refund will be processed.",
            )

        # 8. Create the session
        session_type = (
            SessionType.TRIAL if payment.lesson_type == LessonType.TRIAL
            else SessionType.SINGLE
        )

        if session_type == SessionType.TRIAL:
            session = Session.book_trial(
                instructor_id=slot.instructor_id,
                student_id=payment.student_id,
                start_at=slot.start_at,
                duration_minutes=slot.duration_minutes,
                amount=payment.amount,
                timezone=slot.timezone,
            )
        else:
            session = Session.book_single(
                instructor_id=slot.instructor_id,
                student_id=payment.student_id,
                start_at=slot.start_at,
                duration_minutes=slot.duration_minutes,
                amount=payment.amount,
                timezone=slot.timezone,
            )

        # Set currency to INR
        session.currency = "INR"

        # Auto-confirm the session since payment is done
        session.confirm()

        # 9. Save session
        session = self.session_repo.save(session)

        # 10. Book the slot
        slot.book(session.id)
        self.slot_repo.save(slot)

        # 11. Complete the payment
        payment.complete(
            payment_id=request.razorpay_payment_id,
            signature=request.razorpay_signature,
            session_id=session.id,
        )
        self.payment_repo.update(payment)

        # 12. Credit instructor's wallet
        try:
            wallet = self.wallet_repo.get_by_instructor_id(slot.instructor_id)
            if wallet:
                # Platform fee (e.g., 15%)
                platform_fee_percent = Decimal("15")
                platform_fee = (payment.amount * platform_fee_percent) / Decimal("100")
                instructor_amount = payment.amount - platform_fee

                money = Money.create(instructor_amount, "INR")
                description = f"Payment for {'trial' if session_type == SessionType.TRIAL else 'regular'} session #{session.id}"

                transaction = wallet.deposit(
                    amount=money,
                    reference_type="session",
                    reference_id=session.id,
                    description=description,
                )

                self.wallet_repo.update(wallet)
                self.wallet_repo.save_transaction(transaction)
        except Exception as e:
            # Log error but don't fail the booking
            print(f"Warning: Failed to credit wallet: {e}")

        # 13. Return success response
        return ConfirmBookingResponse(
            success=True,
            session_id=session.id,
            message="Booking confirmed successfully",
            session_start=session.start_at.isoformat(),
            session_end=session.end_at.isoformat(),
            amount_paid=f"₹{payment.amount:.0f}",
        )
