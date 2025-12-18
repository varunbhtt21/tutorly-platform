"""
Initiate Booking Use Case.

Step 1 of the booking flow: Creates a payment order for lesson booking.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.domains.payment.entities.payment import Payment
from app.domains.payment.value_objects.enums import LessonType
from app.domains.payment.value_objects.payment_intent import PaymentIntent
from app.domains.payment.repositories.payment_repository import IPaymentRepository
from app.domains.payment.services.payment_gateway import (
    IPaymentGateway,
    GatewayOrder,
    PaymentGatewayError,
)
from app.domains.scheduling.repositories.booking_slot_repository import IBookingSlotRepository
from app.domains.scheduling.entities import BookingSlot
from app.domains.instructor.repositories import IInstructorProfileRepository


@dataclass
class InitiateBookingRequest:
    """
    Request to initiate a booking.

    Supports two modes:
    1. Booking an existing one-time slot: Provide slot_id
    2. Booking from recurring availability: Provide availability_rule_id + start_at + end_at + duration_minutes
    """

    student_id: int
    instructor_id: int
    lesson_type: str = "trial"  # "trial" or "regular"

    # Option 1: Existing slot ID (for one-time availability)
    slot_id: Optional[int] = None

    # Option 2: Recurring availability info (for dynamically generated slots)
    availability_rule_id: Optional[int] = None
    start_at: Optional[str] = None  # ISO format datetime
    end_at: Optional[str] = None    # ISO format datetime
    duration_minutes: Optional[int] = None


@dataclass
class InitiateBookingResponse:
    """Response from initiate booking."""

    payment_id: int
    razorpay_order_id: str
    razorpay_key: str
    amount: int  # In paise
    currency: str
    instructor_name: str
    slot_start: str
    slot_end: str
    description: str


class InitiateBookingUseCase:
    """
    Use case for initiating a lesson booking.

    This is Step 1 of the booking flow:
    1. Validates the slot is available
    2. Gets instructor pricing
    3. Creates a payment record
    4. Creates a Razorpay order
    5. Returns order details for frontend checkout

    The slot is NOT reserved at this stage - it's reserved only
    when payment processing starts.
    """

    def __init__(
        self,
        payment_repo: IPaymentRepository,
        slot_repo: IBookingSlotRepository,
        instructor_repo: IInstructorProfileRepository,
        payment_gateway: IPaymentGateway,
    ):
        """
        Initialize use case with dependencies.

        Args:
            payment_repo: Payment repository
            slot_repo: Booking slot repository
            instructor_repo: Instructor profile repository
            payment_gateway: Payment gateway (Razorpay)
        """
        self.payment_repo = payment_repo
        self.slot_repo = slot_repo
        self.instructor_repo = instructor_repo
        self.payment_gateway = payment_gateway

    def execute(self, request: InitiateBookingRequest) -> InitiateBookingResponse:
        """
        Execute the initiate booking use case.

        Args:
            request: Booking initiation request

        Returns:
            InitiateBookingResponse with payment order details

        Raises:
            ValueError: If slot not available or validation fails
            PaymentGatewayError: If gateway order creation fails
        """
        # 1. Get or create the booking slot
        slot = self._get_or_create_slot(request)

        if not slot.is_available:
            raise ValueError(f"Slot is not available (status: {slot.status.value})")

        # 2. Check if there's already a pending payment for this slot
        existing_payment = self.payment_repo.get_pending_for_slot(slot.id)
        if existing_payment:
            raise ValueError("This slot already has a pending payment")

        # 3. Get instructor profile and user data for pricing and instructor name
        instructor_result = self.instructor_repo.get_with_user(slot.instructor_id)
        if not instructor_result:
            raise ValueError(f"Instructor {slot.instructor_id} not found")

        profile, user = instructor_result
        instructor_name = f"{user.first_name} {user.last_name}"

        # 4. Determine lesson type and amount
        lesson_type = LessonType(request.lesson_type)

        if not profile.pricing:
            raise ValueError("Instructor has not set pricing")

        if lesson_type == LessonType.TRIAL:
            if not profile.pricing.trial_session_price:
                raise ValueError("Instructor has not set trial lesson price")
            amount = profile.pricing.trial_session_price
        else:
            if not profile.pricing.regular_session_price:
                raise ValueError("Instructor has not set regular session price")
            # Calculate based on slot duration (regular_session_price is for 50 min session)
            amount = (profile.pricing.regular_session_price * Decimal(slot.duration_minutes)) / Decimal(50)

        # 5. Create payment intent
        intent = PaymentIntent(
            student_id=request.student_id,
            instructor_id=request.instructor_id,
            slot_id=slot.id,
            lesson_type=lesson_type,
            amount=Decimal(str(amount)),
            currency="INR",
            description=f"{'Trial' if lesson_type == LessonType.TRIAL else 'Regular'} lesson with {instructor_name}",
        )

        # 6. Create payment entity
        payment = Payment.create_from_intent(intent)

        # 7. Save payment (to get ID)
        payment = self.payment_repo.save(payment)

        # 8. Get student info for prefill (optional)
        prefill_name = None
        prefill_email = None
        prefill_contact = None

        # 9. Create Razorpay order
        try:
            gateway_order = self.payment_gateway.create_order(
                amount=intent.amount,
                currency=intent.currency,
                receipt=f"payment_{payment.id}",
                notes={
                    "payment_id": payment.id,
                    "student_id": request.student_id,
                    "instructor_id": request.instructor_id,
                    "slot_id": slot.id,
                    "lesson_type": lesson_type.value,
                    "description": intent.description,
                },
                prefill_name=prefill_name,
                prefill_email=prefill_email,
                prefill_contact=prefill_contact,
            )
        except PaymentGatewayError as e:
            # Mark payment as failed
            payment.fail(f"Gateway order creation failed: {e.message}")
            self.payment_repo.update(payment)
            raise

        # 10. Update payment with gateway order ID
        payment.set_gateway_order(gateway_order.order_id)
        self.payment_repo.update(payment)

        # 11. Return response
        return InitiateBookingResponse(
            payment_id=payment.id,
            razorpay_order_id=gateway_order.order_id,
            razorpay_key=gateway_order.key,
            amount=gateway_order.amount,
            currency=gateway_order.currency,
            instructor_name=instructor_name,
            slot_start=slot.start_at.isoformat(),
            slot_end=slot.end_at.isoformat(),
            description=intent.description or "",
        )

    def _get_or_create_slot(self, request: InitiateBookingRequest) -> BookingSlot:
        """
        Get an existing slot or create a new one for recurring availability.

        For one-time availability: slot already exists in the database, just fetch it.
        For recurring availability: create a new booking slot on-the-fly.

        Args:
            request: Booking initiation request

        Returns:
            BookingSlot entity

        Raises:
            ValueError: If slot not found or invalid request data
        """
        # Mode 1: Existing slot ID (one-time availability)
        if request.slot_id is not None:
            slot = self.slot_repo.get_by_id(request.slot_id)
            if not slot:
                raise ValueError(f"Slot {request.slot_id} not found")
            return slot

        # Mode 2: Recurring availability - create slot on-the-fly
        if not all([request.availability_rule_id, request.start_at, request.end_at, request.duration_minutes]):
            raise ValueError(
                "For recurring availability booking, must provide: "
                "availability_rule_id, start_at, end_at, and duration_minutes"
            )

        # Parse datetime strings
        try:
            start_at = datetime.fromisoformat(request.start_at)
            end_at = datetime.fromisoformat(request.end_at)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid datetime format: {e}")

        # Check if a slot already exists for this time (avoid duplicates)
        existing_slot = self.slot_repo.get_by_instructor_and_time(
            instructor_id=request.instructor_id,
            start_at=start_at,
        )
        if existing_slot:
            return existing_slot

        # Create new booking slot for recurring availability
        slot = BookingSlot.create(
            instructor_id=request.instructor_id,
            availability_rule_id=request.availability_rule_id,
            start_at=start_at,
            end_at=end_at,
            duration_minutes=request.duration_minutes,
            timezone="UTC",  # Default timezone
        )

        # Save the slot to get an ID
        slot = self.slot_repo.save(slot)

        return slot
