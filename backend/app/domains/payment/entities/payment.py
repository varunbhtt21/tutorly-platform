"""
Payment Aggregate Root.

The Payment entity is the aggregate root for the payment domain.
It encapsulates all payment logic and ensures consistency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.domains.payment.value_objects.enums import (
    PaymentStatus,
    PaymentMethod,
    PaymentGateway,
    LessonType,
)
from app.domains.payment.value_objects.payment_intent import PaymentIntent


@dataclass
class Payment:
    """
    Payment Aggregate Root.

    Represents a payment transaction for a lesson booking.
    Handles the complete lifecycle of a payment from initiation to completion.

    Attributes:
        id: Unique payment identifier
        student_id: ID of the student making payment
        instructor_id: ID of the instructor being paid
        session_id: ID of the session (linked after booking confirmed)
        slot_id: ID of the availability slot being booked
        amount: Payment amount
        currency: Currency code (default INR)
        status: Current payment status
        lesson_type: Type of lesson (trial/regular)
        payment_method: Method used (upi/card/etc.)
        gateway: Payment gateway used
        gateway_order_id: Gateway's order reference
        gateway_payment_id: Gateway's payment reference
        gateway_signature: Signature for verification
        failure_reason: Reason if payment failed
        extra_data: Additional metadata
        created_at: When payment was created
        updated_at: When payment was last updated
        completed_at: When payment was completed
    """

    # Core identifiers
    id: Optional[int] = None
    student_id: int = 0
    instructor_id: int = 0
    session_id: Optional[int] = None
    slot_id: int = 0

    # Payment details
    amount: Decimal = Decimal("0.00")
    currency: str = "INR"
    status: PaymentStatus = PaymentStatus.PENDING
    lesson_type: LessonType = LessonType.TRIAL

    # Payment method
    payment_method: Optional[PaymentMethod] = None
    gateway: PaymentGateway = PaymentGateway.RAZORPAY

    # Gateway references
    gateway_order_id: Optional[str] = None
    gateway_payment_id: Optional[str] = None
    gateway_signature: Optional[str] = None

    # Error tracking
    failure_reason: Optional[str] = None

    # Metadata
    extra_data: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Domain events
    _domain_events: List[Any] = field(default_factory=list, repr=False)

    # ----- Factory Methods -----

    @classmethod
    def create_from_intent(
        cls,
        intent: PaymentIntent,
        gateway: PaymentGateway = PaymentGateway.RAZORPAY,
    ) -> "Payment":
        """
        Create a new payment from a PaymentIntent.

        Args:
            intent: PaymentIntent value object with booking details
            gateway: Payment gateway to use

        Returns:
            New Payment entity in PENDING status
        """
        payment = cls(
            student_id=intent.student_id,
            instructor_id=intent.instructor_id,
            slot_id=intent.slot_id,
            amount=intent.amount,
            currency=intent.currency,
            status=PaymentStatus.PENDING,
            lesson_type=intent.lesson_type,
            gateway=gateway,
            description=intent.description,
            extra_data=intent.to_dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Emit domain event
        from app.domains.payment.events.payment_events import PaymentInitiated
        payment._domain_events.append(
            PaymentInitiated(
                payment_id=payment.id,
                student_id=payment.student_id,
                instructor_id=payment.instructor_id,
                amount=payment.amount,
                currency=payment.currency,
            )
        )

        return payment

    # ----- Business Methods -----

    def set_gateway_order(self, order_id: str) -> None:
        """
        Set the gateway order ID after creating order with payment gateway.

        Args:
            order_id: The order ID from the payment gateway
        """
        if self.status != PaymentStatus.PENDING:
            raise ValueError(f"Cannot set order for payment in {self.status.value} status")

        self.gateway_order_id = order_id
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def set_payment_method(self, method: PaymentMethod) -> None:
        """
        Set the payment method used.

        Args:
            method: Payment method (UPI, Card, etc.)
        """
        self.payment_method = method
        self.updated_at = datetime.utcnow()

    def complete(
        self,
        payment_id: str,
        signature: str,
        session_id: int,
    ) -> None:
        """
        Mark payment as completed after successful verification.

        Args:
            payment_id: Gateway payment ID
            signature: Gateway signature for verification
            session_id: ID of the created session

        Raises:
            ValueError: If payment is not in PROCESSING status
        """
        if self.status != PaymentStatus.PROCESSING:
            raise ValueError(
                f"Cannot complete payment in {self.status.value} status. "
                f"Payment must be in PROCESSING status."
            )

        self.gateway_payment_id = payment_id
        self.gateway_signature = signature
        self.session_id = session_id
        self.status = PaymentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Emit domain event
        from app.domains.payment.events.payment_events import PaymentCompleted
        self._domain_events.append(
            PaymentCompleted(
                payment_id=self.id,
                session_id=session_id,
                student_id=self.student_id,
                instructor_id=self.instructor_id,
                amount=self.amount,
                currency=self.currency,
            )
        )

    def fail(self, reason: str) -> None:
        """
        Mark payment as failed.

        Args:
            reason: Reason for failure
        """
        if self.status == PaymentStatus.COMPLETED:
            raise ValueError("Cannot fail a completed payment. Use refund instead.")

        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.updated_at = datetime.utcnow()

        # Emit domain event
        from app.domains.payment.events.payment_events import PaymentFailed
        self._domain_events.append(
            PaymentFailed(
                payment_id=self.id,
                student_id=self.student_id,
                reason=reason,
            )
        )

    def cancel(self) -> None:
        """
        Cancel a pending payment.

        Only payments in PENDING or PROCESSING status can be cancelled.
        """
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError(
                f"Cannot cancel payment in {self.status.value} status. "
                f"Only PENDING or PROCESSING payments can be cancelled."
            )

        self.status = PaymentStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def refund(self, refund_id: Optional[str] = None) -> None:
        """
        Refund a completed payment.

        Args:
            refund_id: Optional gateway refund ID

        Raises:
            ValueError: If payment is not COMPLETED
        """
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError(
                f"Cannot refund payment in {self.status.value} status. "
                f"Only COMPLETED payments can be refunded."
            )

        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.utcnow()

        if refund_id:
            self.extra_data["refund_id"] = refund_id

        # Emit domain event
        from app.domains.payment.events.payment_events import PaymentRefunded
        self._domain_events.append(
            PaymentRefunded(
                payment_id=self.id,
                student_id=self.student_id,
                instructor_id=self.instructor_id,
                amount=self.amount,
                currency=self.currency,
            )
        )

    # ----- Query Methods -----

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == PaymentStatus.PENDING

    @property
    def is_processing(self) -> bool:
        """Check if payment is processing."""
        return self.status == PaymentStatus.PROCESSING

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED

    @property
    def is_refunded(self) -> bool:
        """Check if payment is refunded."""
        return self.status == PaymentStatus.REFUNDED

    @property
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def amount_in_paise(self) -> int:
        """Get amount in paise for Razorpay."""
        return int(self.amount * 100)

    # ----- Domain Events -----

    def get_domain_events(self) -> List[Any]:
        """Get all domain events."""
        return list(self._domain_events)

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    # ----- String Representation -----

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Payment(id={self.id}, student={self.student_id}, "
            f"amount=₹{self.amount:.2f}, status={self.status.value})"
        )
