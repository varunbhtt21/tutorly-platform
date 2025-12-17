"""
Payment Mapper.

Maps between Payment domain entity and Payment ORM model.
Following the Data Mapper pattern from DDD.
"""

import json
from decimal import Decimal
from typing import Any, Dict

from app.domains.payment.entities.payment import Payment
from app.domains.payment.value_objects.enums import (
    PaymentStatus,
    PaymentMethod,
    PaymentGateway,
    LessonType,
)
from app.database.models import (
    Payment as PaymentORM,
    PaymentStatus as PaymentStatusORM,
    PaymentMethod as PaymentMethodORM,
    PaymentGateway as PaymentGatewayORM,
    LessonType as LessonTypeORM,
)


class PaymentMapper:
    """
    Mapper for converting between Payment domain entity and ORM model.

    Handles the translation of domain concepts to persistence layer
    and vice versa, maintaining separation of concerns.
    """

    @staticmethod
    def to_domain(orm_payment: PaymentORM) -> Payment:
        """
        Convert ORM model to domain entity.

        Args:
            orm_payment: SQLAlchemy Payment model

        Returns:
            Payment domain entity
        """
        # Parse extra_data from JSON string
        extra_data = {}
        if orm_payment.extra_data:
            try:
                extra_data = json.loads(orm_payment.extra_data)
            except (json.JSONDecodeError, TypeError):
                extra_data = {}

        # Map payment method (can be None)
        payment_method = None
        if orm_payment.payment_method:
            payment_method = PaymentMethod(orm_payment.payment_method.value)

        return Payment(
            id=orm_payment.id,
            student_id=orm_payment.student_id,
            instructor_id=orm_payment.instructor_id,
            session_id=orm_payment.session_id,
            slot_id=orm_payment.slot_id,
            amount=Decimal(str(orm_payment.amount)) if orm_payment.amount else Decimal("0.00"),
            currency=orm_payment.currency,
            status=PaymentStatus(orm_payment.status.value),
            lesson_type=LessonType(orm_payment.lesson_type.value),
            payment_method=payment_method,
            gateway=PaymentGateway(orm_payment.gateway.value),
            gateway_order_id=orm_payment.gateway_order_id,
            gateway_payment_id=orm_payment.gateway_payment_id,
            gateway_signature=orm_payment.gateway_signature,
            failure_reason=orm_payment.failure_reason,
            description=orm_payment.description,
            extra_data=extra_data,
            created_at=orm_payment.created_at,
            updated_at=orm_payment.updated_at,
            completed_at=orm_payment.completed_at,
        )

    @staticmethod
    def to_persistence(payment: Payment) -> Dict[str, Any]:
        """
        Convert domain entity to persistence dict for updates.

        Args:
            payment: Payment domain entity

        Returns:
            Dict suitable for ORM model update
        """
        # Serialize extra_data to JSON string
        extra_data_str = None
        if payment.extra_data:
            extra_data_str = json.dumps(payment.extra_data)

        # Map payment method
        payment_method_orm = None
        if payment.payment_method:
            payment_method_orm = PaymentMethodORM(payment.payment_method.value)

        return {
            "student_id": payment.student_id,
            "instructor_id": payment.instructor_id,
            "session_id": payment.session_id,
            "slot_id": payment.slot_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": PaymentStatusORM(payment.status.value),
            "lesson_type": LessonTypeORM(payment.lesson_type.value),
            "payment_method": payment_method_orm,
            "gateway": PaymentGatewayORM(payment.gateway.value),
            "gateway_order_id": payment.gateway_order_id,
            "gateway_payment_id": payment.gateway_payment_id,
            "gateway_signature": payment.gateway_signature,
            "failure_reason": payment.failure_reason,
            "description": payment.description,
            "extra_data": extra_data_str,
            "completed_at": payment.completed_at,
        }

    @staticmethod
    def create_orm_instance(payment: Payment) -> PaymentORM:
        """
        Create new ORM instance from domain entity.

        Args:
            payment: Payment domain entity

        Returns:
            New PaymentORM instance
        """
        # Serialize extra_data to JSON string
        extra_data_str = None
        if payment.extra_data:
            extra_data_str = json.dumps(payment.extra_data)

        # Map payment method
        payment_method_orm = None
        if payment.payment_method:
            payment_method_orm = PaymentMethodORM(payment.payment_method.value)

        return PaymentORM(
            student_id=payment.student_id,
            instructor_id=payment.instructor_id,
            session_id=payment.session_id,
            slot_id=payment.slot_id,
            amount=payment.amount,
            currency=payment.currency,
            status=PaymentStatusORM(payment.status.value),
            lesson_type=LessonTypeORM(payment.lesson_type.value),
            payment_method=payment_method_orm,
            gateway=PaymentGatewayORM(payment.gateway.value),
            gateway_order_id=payment.gateway_order_id,
            gateway_payment_id=payment.gateway_payment_id,
            gateway_signature=payment.gateway_signature,
            failure_reason=payment.failure_reason,
            description=payment.description,
            extra_data=extra_data_str,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            completed_at=payment.completed_at,
        )
