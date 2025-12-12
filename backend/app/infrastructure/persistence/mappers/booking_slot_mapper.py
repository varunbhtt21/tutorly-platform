"""Mapper for BookingSlot domain entity <-> SQLAlchemy model."""

from app.domains.scheduling.entities import BookingSlot, SlotStatus
from app.infrastructure.persistence.sqlalchemy_models import BookingSlot as BookingSlotModel


class BookingSlotMapper:
    """Maps between BookingSlot domain entity and SQLAlchemy model."""

    @staticmethod
    def to_domain(db_model: BookingSlotModel) -> BookingSlot:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            db_model: The SQLAlchemy BookingSlot model

        Returns:
            BookingSlot domain entity
        """
        return BookingSlot(
            id=db_model.id,
            instructor_id=db_model.instructor_id,
            availability_rule_id=db_model.availability_rule_id,
            start_at=db_model.start_at,
            end_at=db_model.end_at,
            duration_minutes=db_model.duration_minutes,
            status=SlotStatus(db_model.status),
            session_id=db_model.session_id,
            timezone=db_model.timezone,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )

    @staticmethod
    def to_orm(domain_entity: BookingSlot) -> BookingSlotModel:
        """
        Convert domain entity to SQLAlchemy model (for creating new records).

        Args:
            domain_entity: The BookingSlot domain entity

        Returns:
            SQLAlchemy BookingSlot model
        """
        return BookingSlotModel(
            id=domain_entity.id,
            instructor_id=domain_entity.instructor_id,
            availability_rule_id=domain_entity.availability_rule_id,
            start_at=domain_entity.start_at,
            end_at=domain_entity.end_at,
            duration_minutes=domain_entity.duration_minutes,
            status=domain_entity.status.value,
            session_id=domain_entity.session_id,
            timezone=domain_entity.timezone,
        )

    @staticmethod
    def update_orm(db_model: BookingSlotModel, domain_entity: BookingSlot) -> BookingSlotModel:
        """
        Update SQLAlchemy model with values from domain entity.

        Args:
            db_model: The existing SQLAlchemy model
            domain_entity: The BookingSlot domain entity with updated values

        Returns:
            Updated SQLAlchemy model
        """
        db_model.start_at = domain_entity.start_at
        db_model.end_at = domain_entity.end_at
        db_model.duration_minutes = domain_entity.duration_minutes
        db_model.status = domain_entity.status.value
        db_model.session_id = domain_entity.session_id
        db_model.timezone = domain_entity.timezone

        return db_model
