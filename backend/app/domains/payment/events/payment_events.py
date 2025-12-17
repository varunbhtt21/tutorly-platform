"""
Payment Domain Events.

Events emitted by the Payment aggregate root.
These events can be used for:
- Event sourcing
- Notifications (email, push)
- Analytics/Reporting
- Saga orchestration
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class PaymentEvent:
    """Base class for payment domain events."""

    event_id: str = field(default_factory=lambda: f"evt_{datetime.utcnow().timestamp()}")
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PaymentInitiated(PaymentEvent):
    """
    Event emitted when a payment is initiated.

    This happens when a student starts the checkout process
    and a payment record is created.
    """

    payment_id: Optional[int] = None
    student_id: int = 0
    instructor_id: int = 0
    amount: Decimal = Decimal("0.00")
    currency: str = "INR"


@dataclass(frozen=True)
class PaymentCompleted(PaymentEvent):
    """
    Event emitted when a payment is successfully completed.

    This triggers:
    - Session creation
    - Slot booking confirmation
    - Instructor wallet credit
    - Confirmation notifications
    """

    payment_id: Optional[int] = None
    session_id: Optional[int] = None
    student_id: int = 0
    instructor_id: int = 0
    amount: Decimal = Decimal("0.00")
    currency: str = "INR"


@dataclass(frozen=True)
class PaymentFailed(PaymentEvent):
    """
    Event emitted when a payment fails.

    This triggers:
    - Slot release
    - Failure notification to student
    """

    payment_id: Optional[int] = None
    student_id: int = 0
    reason: str = ""


@dataclass(frozen=True)
class PaymentRefunded(PaymentEvent):
    """
    Event emitted when a payment is refunded.

    This triggers:
    - Session cancellation
    - Wallet debit (if already credited)
    - Refund notification
    """

    payment_id: Optional[int] = None
    student_id: int = 0
    instructor_id: int = 0
    amount: Decimal = Decimal("0.00")
    currency: str = "INR"
    refund_reason: Optional[str] = None
