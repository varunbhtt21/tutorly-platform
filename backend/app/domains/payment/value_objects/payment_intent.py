"""
Payment Intent Value Object.

Represents the intent to make a payment for a booking.
Immutable value object that captures all necessary information
for initiating a payment.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domains.payment.value_objects.enums import LessonType


@dataclass(frozen=True)
class PaymentIntent:
    """
    Value object representing intent to pay for a lesson booking.

    Immutable and validated at creation time.

    Attributes:
        student_id: ID of the student making the payment
        instructor_id: ID of the instructor being booked
        slot_id: ID of the availability slot being booked
        lesson_type: Type of lesson (trial or regular)
        amount: Payment amount in smallest currency unit
        currency: Currency code (default INR)
        description: Human-readable description
    """

    student_id: int
    instructor_id: int
    slot_id: int
    lesson_type: LessonType
    amount: Decimal
    currency: str = "INR"
    description: Optional[str] = None

    def __post_init__(self):
        """Validate payment intent on creation."""
        if self.student_id <= 0:
            raise ValueError("student_id must be positive")
        if self.instructor_id <= 0:
            raise ValueError("instructor_id must be positive")
        if self.slot_id <= 0:
            raise ValueError("slot_id must be positive")
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if self.student_id == self.instructor_id:
            raise ValueError("Student cannot book their own lesson")

    @classmethod
    def create_trial_intent(
        cls,
        student_id: int,
        instructor_id: int,
        slot_id: int,
        trial_price: Decimal,
        instructor_name: str = "",
    ) -> "PaymentIntent":
        """
        Factory method to create a trial lesson payment intent.

        Args:
            student_id: ID of the student
            instructor_id: ID of the instructor
            slot_id: ID of the slot to book
            trial_price: Trial lesson price
            instructor_name: Name of instructor for description

        Returns:
            PaymentIntent for trial lesson
        """
        description = f"Trial lesson with {instructor_name}" if instructor_name else "Trial lesson"
        return cls(
            student_id=student_id,
            instructor_id=instructor_id,
            slot_id=slot_id,
            lesson_type=LessonType.TRIAL,
            amount=trial_price,
            currency="INR",
            description=description,
        )

    @classmethod
    def create_regular_intent(
        cls,
        student_id: int,
        instructor_id: int,
        slot_id: int,
        hourly_rate: Decimal,
        duration_minutes: int = 60,
        instructor_name: str = "",
    ) -> "PaymentIntent":
        """
        Factory method to create a regular lesson payment intent.

        Args:
            student_id: ID of the student
            instructor_id: ID of the instructor
            slot_id: ID of the slot to book
            hourly_rate: Instructor's hourly rate
            duration_minutes: Lesson duration in minutes
            instructor_name: Name of instructor for description

        Returns:
            PaymentIntent for regular lesson
        """
        # Calculate amount based on duration
        amount = (hourly_rate * Decimal(duration_minutes)) / Decimal(60)
        description = f"{duration_minutes} min lesson with {instructor_name}" if instructor_name else f"{duration_minutes} min lesson"

        return cls(
            student_id=student_id,
            instructor_id=instructor_id,
            slot_id=slot_id,
            lesson_type=LessonType.REGULAR,
            amount=amount,
            currency="INR",
            description=description,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "student_id": self.student_id,
            "instructor_id": self.instructor_id,
            "slot_id": self.slot_id,
            "lesson_type": self.lesson_type.value,
            "amount": str(self.amount),
            "currency": self.currency,
            "description": self.description,
        }

    @property
    def amount_in_paise(self) -> int:
        """
        Get amount in paise (smallest currency unit for INR).
        Razorpay requires amount in paise.
        """
        return int(self.amount * 100)
