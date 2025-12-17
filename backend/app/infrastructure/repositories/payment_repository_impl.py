"""
Payment Repository Implementation.

SQLAlchemy implementation of the IPaymentRepository interface.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session as DBSession

from app.domains.payment.entities.payment import Payment
from app.domains.payment.repositories.payment_repository import IPaymentRepository
from app.domains.payment.value_objects.enums import PaymentStatus
from app.database.models import (
    Payment as PaymentORM,
    PaymentStatus as PaymentStatusORM,
)
from app.infrastructure.persistence.mappers.payment_mapper import PaymentMapper


class PaymentRepositoryImpl(IPaymentRepository):
    """
    SQLAlchemy implementation of Payment Repository.

    Handles all payment persistence operations using SQLAlchemy ORM.
    """

    def __init__(self, db: DBSession):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def save(self, payment: Payment) -> Payment:
        """
        Save a new payment.

        Args:
            payment: Payment entity to save

        Returns:
            Saved payment with ID assigned
        """
        orm_payment = PaymentMapper.create_orm_instance(payment)
        self.db.add(orm_payment)
        self.db.commit()
        self.db.refresh(orm_payment)

        return PaymentMapper.to_domain(orm_payment)

    def update(self, payment: Payment) -> Payment:
        """
        Update an existing payment.

        Args:
            payment: Payment entity to update

        Returns:
            Updated payment
        """
        orm_payment = self.db.query(PaymentORM).filter(
            PaymentORM.id == payment.id
        ).first()

        if not orm_payment:
            raise ValueError(f"Payment with id {payment.id} not found")

        # Update fields
        update_data = PaymentMapper.to_persistence(payment)
        for key, value in update_data.items():
            setattr(orm_payment, key, value)

        orm_payment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(orm_payment)

        return PaymentMapper.to_domain(orm_payment)

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Get payment by ID.

        Args:
            payment_id: Payment identifier

        Returns:
            Payment if found, None otherwise
        """
        orm_payment = self.db.query(PaymentORM).filter(
            PaymentORM.id == payment_id
        ).first()

        if not orm_payment:
            return None

        return PaymentMapper.to_domain(orm_payment)

    def get_by_gateway_order_id(self, order_id: str) -> Optional[Payment]:
        """
        Get payment by gateway order ID.

        Args:
            order_id: Gateway's order reference

        Returns:
            Payment if found, None otherwise
        """
        orm_payment = self.db.query(PaymentORM).filter(
            PaymentORM.gateway_order_id == order_id
        ).first()

        if not orm_payment:
            return None

        return PaymentMapper.to_domain(orm_payment)

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
        query = self.db.query(PaymentORM).filter(
            PaymentORM.student_id == student_id
        )

        if status:
            query = query.filter(
                PaymentORM.status == PaymentStatusORM(status.value)
            )

        query = query.order_by(PaymentORM.created_at.desc())
        query = query.offset(offset).limit(limit)

        orm_payments = query.all()
        return [PaymentMapper.to_domain(p) for p in orm_payments]

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
        query = self.db.query(PaymentORM).filter(
            PaymentORM.instructor_id == instructor_id
        )

        if status:
            query = query.filter(
                PaymentORM.status == PaymentStatusORM(status.value)
            )

        query = query.order_by(PaymentORM.created_at.desc())
        query = query.offset(offset).limit(limit)

        orm_payments = query.all()
        return [PaymentMapper.to_domain(p) for p in orm_payments]

    def get_pending_for_slot(self, slot_id: int) -> Optional[Payment]:
        """
        Get pending/processing payment for a specific slot.

        Used to check if a slot is already reserved.

        Args:
            slot_id: Slot identifier

        Returns:
            Pending/processing payment if exists, None otherwise
        """
        orm_payment = self.db.query(PaymentORM).filter(
            PaymentORM.slot_id == slot_id,
            PaymentORM.status.in_([
                PaymentStatusORM.PENDING,
                PaymentStatusORM.PROCESSING
            ])
        ).first()

        if not orm_payment:
            return None

        return PaymentMapper.to_domain(orm_payment)

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
        threshold = datetime.utcnow() - timedelta(minutes=minutes)

        orm_payments = self.db.query(PaymentORM).filter(
            PaymentORM.status == PaymentStatusORM.PROCESSING,
            PaymentORM.created_at < threshold
        ).all()

        return [PaymentMapper.to_domain(p) for p in orm_payments]

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
        query = self.db.query(PaymentORM).filter(
            PaymentORM.student_id == student_id
        )

        if status:
            query = query.filter(
                PaymentORM.status == PaymentStatusORM(status.value)
            )

        return query.count()
