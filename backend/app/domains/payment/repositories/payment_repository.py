"""
Payment Repository Interface.

Defines the contract for payment persistence operations.
Following the repository pattern from DDD.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.payment.entities.payment import Payment
from app.domains.payment.value_objects.enums import PaymentStatus


class IPaymentRepository(ABC):
    """
    Payment Repository Interface (Port).

    Defines the contract for payment persistence.
    Implementations (adapters) will handle actual database operations.
    """

    @abstractmethod
    def save(self, payment: Payment) -> Payment:
        """
        Save a new payment.

        Args:
            payment: Payment entity to save

        Returns:
            Saved payment with ID assigned
        """
        pass

    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        """
        Update an existing payment.

        Args:
            payment: Payment entity to update

        Returns:
            Updated payment
        """
        pass

    @abstractmethod
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Get payment by ID.

        Args:
            payment_id: Payment identifier

        Returns:
            Payment if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_gateway_order_id(self, order_id: str) -> Optional[Payment]:
        """
        Get payment by gateway order ID.

        Args:
            order_id: Gateway's order reference

        Returns:
            Payment if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_student_id(
        self,
        student_id: int,
        status: Optional[PaymentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Payment]:
        """
        Get payments by student ID.

        Args:
            student_id: Student identifier
            status: Optional filter by status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of payments
        """
        pass

    @abstractmethod
    def get_by_instructor_id(
        self,
        instructor_id: int,
        status: Optional[PaymentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Payment]:
        """
        Get payments by instructor ID.

        Args:
            instructor_id: Instructor identifier
            status: Optional filter by status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of payments
        """
        pass

    @abstractmethod
    def get_pending_for_slot(self, slot_id: int) -> Optional[Payment]:
        """
        Get pending payment for a specific slot.

        Used to check if a slot is already reserved.

        Args:
            slot_id: Slot identifier

        Returns:
            Pending payment if exists, None otherwise
        """
        pass

    @abstractmethod
    def get_processing_payments_older_than(
        self,
        minutes: int,
    ) -> List[Payment]:
        """
        Get processing payments older than specified minutes.

        Used to find stale payments that should be cancelled.

        Args:
            minutes: Age threshold in minutes

        Returns:
            List of stale processing payments
        """
        pass

    @abstractmethod
    def count_by_student_id(
        self,
        student_id: int,
        status: Optional[PaymentStatus] = None,
    ) -> int:
        """
        Count payments by student ID.

        Args:
            student_id: Student identifier
            status: Optional filter by status

        Returns:
            Count of payments
        """
        pass
