"""Mapper for Availability domain entity <-> SQLAlchemy model."""

from datetime import date, time
from typing import Optional

from app.domains.scheduling.entities import Availability
from app.domains.scheduling.value_objects import AvailabilityType, DayOfWeek
from app.infrastructure.persistence.sqlalchemy_models import AvailabilitySlot


class AvailabilityMapper:
    """Maps between Availability domain entity and SQLAlchemy model."""

    @staticmethod
    def to_domain(db_model: AvailabilitySlot) -> Availability:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            db_model: The SQLAlchemy AvailabilitySlot model

        Returns:
            Availability domain entity
        """
        # Parse day of week
        day_of_week = None
        if db_model.day_of_week is not None:
            day_of_week = DayOfWeek.from_int(db_model.day_of_week)

        # Parse specific date
        specific_date = None
        if db_model.specific_date:
            specific_date = date.fromisoformat(db_model.specific_date)

        # Parse times
        start_time = time.fromisoformat(db_model.start_time)
        end_time = time.fromisoformat(db_model.end_time)

        # Parse dates
        valid_from = date.fromisoformat(db_model.valid_from)
        valid_until = None
        if db_model.valid_until:
            valid_until = date.fromisoformat(db_model.valid_until)

        return Availability(
            id=db_model.id,
            instructor_id=db_model.instructor_id,
            availability_type=AvailabilityType(db_model.availability_type),
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            specific_date=specific_date,
            slot_duration_minutes=db_model.slot_duration_minutes,
            break_minutes=db_model.break_minutes,
            valid_from=valid_from,
            valid_until=valid_until,
            timezone=db_model.timezone,
            is_active=db_model.is_active,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )

    @staticmethod
    def to_orm(domain_entity: Availability) -> AvailabilitySlot:
        """
        Convert domain entity to SQLAlchemy model (for creating new records).

        Args:
            domain_entity: The Availability domain entity

        Returns:
            SQLAlchemy AvailabilitySlot model
        """
        return AvailabilitySlot(
            id=domain_entity.id,
            instructor_id=domain_entity.instructor_id,
            availability_type=domain_entity.availability_type.value,
            day_of_week=domain_entity.day_of_week.value if domain_entity.day_of_week else None,
            start_time=domain_entity.start_time.isoformat(),
            end_time=domain_entity.end_time.isoformat(),
            specific_date=domain_entity.specific_date.isoformat() if domain_entity.specific_date else None,
            slot_duration_minutes=domain_entity.slot_duration_minutes,
            break_minutes=domain_entity.break_minutes,
            valid_from=domain_entity.valid_from.isoformat(),
            valid_until=domain_entity.valid_until.isoformat() if domain_entity.valid_until else None,
            timezone=domain_entity.timezone,
            is_active=domain_entity.is_active,
        )

    @staticmethod
    def update_orm(db_model: AvailabilitySlot, domain_entity: Availability) -> AvailabilitySlot:
        """
        Update SQLAlchemy model with values from domain entity.

        Args:
            db_model: The existing SQLAlchemy model
            domain_entity: The Availability domain entity with updated values

        Returns:
            Updated SQLAlchemy model
        """
        db_model.availability_type = domain_entity.availability_type.value
        db_model.day_of_week = domain_entity.day_of_week.value if domain_entity.day_of_week else None
        db_model.start_time = domain_entity.start_time.isoformat()
        db_model.end_time = domain_entity.end_time.isoformat()
        db_model.specific_date = domain_entity.specific_date.isoformat() if domain_entity.specific_date else None
        db_model.slot_duration_minutes = domain_entity.slot_duration_minutes
        db_model.break_minutes = domain_entity.break_minutes
        db_model.valid_from = domain_entity.valid_from.isoformat()
        db_model.valid_until = domain_entity.valid_until.isoformat() if domain_entity.valid_until else None
        db_model.timezone = domain_entity.timezone
        db_model.is_active = domain_entity.is_active

        return db_model
