"""Mapper for Session domain entity <-> SQLAlchemy model."""

from decimal import Decimal
from typing import Optional

from app.domains.scheduling.entities import Session as SessionEntity
from app.domains.scheduling.value_objects import SessionStatus, SessionType
from app.infrastructure.persistence.sqlalchemy_models import Session as SessionModel


class SessionMapper:
    """Maps between Session domain entity and SQLAlchemy model."""

    @staticmethod
    def to_domain(db_model: SessionModel) -> SessionEntity:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            db_model: The SQLAlchemy Session model

        Returns:
            Session domain entity
        """
        return SessionEntity(
            id=db_model.id,
            instructor_id=db_model.instructor_id,
            student_id=db_model.student_id,
            start_at=db_model.start_at,
            end_at=db_model.end_at,
            session_type=SessionType(db_model.session_type),
            status=SessionStatus(db_model.status),
            timezone=db_model.timezone,
            subject_id=db_model.subject_id,
            amount=Decimal(str(db_model.amount)) if db_model.amount else Decimal("0.00"),
            currency=db_model.currency,
            parent_session_id=db_model.parent_session_id,
            recurrence_pattern=db_model.recurrence_pattern,
            occurrence_number=db_model.occurrence_number,
            instructor_notes=db_model.instructor_notes,
            student_notes=db_model.student_notes,
            meeting_link=db_model.meeting_link,
            cancelled_at=db_model.cancelled_at,
            cancelled_by=db_model.cancelled_by,
            cancellation_reason=db_model.cancellation_reason,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )

    @staticmethod
    def to_orm(domain_entity: SessionEntity) -> SessionModel:
        """
        Convert domain entity to SQLAlchemy model (for creating new records).

        Args:
            domain_entity: The Session domain entity

        Returns:
            SQLAlchemy Session model
        """
        return SessionModel(
            id=domain_entity.id,
            instructor_id=domain_entity.instructor_id,
            student_id=domain_entity.student_id,
            start_at=domain_entity.start_at,
            end_at=domain_entity.end_at,
            duration_minutes=domain_entity.duration_minutes,
            session_type=domain_entity.session_type.value,
            status=domain_entity.status.value,
            timezone=domain_entity.timezone,
            subject_id=domain_entity.subject_id,
            amount=domain_entity.amount,
            currency=domain_entity.currency,
            parent_session_id=domain_entity.parent_session_id,
            recurrence_pattern=domain_entity.recurrence_pattern,
            occurrence_number=domain_entity.occurrence_number,
            instructor_notes=domain_entity.instructor_notes,
            student_notes=domain_entity.student_notes,
            meeting_link=domain_entity.meeting_link,
            cancelled_at=domain_entity.cancelled_at,
            cancelled_by=domain_entity.cancelled_by,
            cancellation_reason=domain_entity.cancellation_reason,
        )

    @staticmethod
    def update_orm(db_model: SessionModel, domain_entity: SessionEntity) -> SessionModel:
        """
        Update SQLAlchemy model with values from domain entity.

        Args:
            db_model: The existing SQLAlchemy model
            domain_entity: The Session domain entity with updated values

        Returns:
            Updated SQLAlchemy model
        """
        db_model.start_at = domain_entity.start_at
        db_model.end_at = domain_entity.end_at
        db_model.duration_minutes = domain_entity.duration_minutes
        db_model.status = domain_entity.status.value
        db_model.timezone = domain_entity.timezone
        db_model.subject_id = domain_entity.subject_id
        db_model.amount = domain_entity.amount
        db_model.currency = domain_entity.currency
        db_model.instructor_notes = domain_entity.instructor_notes
        db_model.student_notes = domain_entity.student_notes
        db_model.meeting_link = domain_entity.meeting_link
        db_model.cancelled_at = domain_entity.cancelled_at
        db_model.cancelled_by = domain_entity.cancelled_by
        db_model.cancellation_reason = domain_entity.cancellation_reason

        return db_model
