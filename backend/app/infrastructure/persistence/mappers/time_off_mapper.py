"""Mapper for TimeOff domain entity <-> SQLAlchemy model."""

from typing import Optional

from app.domains.scheduling.entities import TimeOff as TimeOffEntity
from app.domains.scheduling.value_objects import DayOfWeek
from app.infrastructure.persistence.sqlalchemy_models import TimeOff as TimeOffModel


class TimeOffMapper:
    """Maps between TimeOff domain entity and SQLAlchemy model."""

    @staticmethod
    def to_domain(db_model: TimeOffModel) -> TimeOffEntity:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            db_model: The SQLAlchemy TimeOff model

        Returns:
            TimeOff domain entity
        """
        recurrence_day = None
        if db_model.recurrence_day is not None:
            recurrence_day = DayOfWeek.from_int(db_model.recurrence_day)

        return TimeOffEntity(
            id=db_model.id,
            instructor_id=db_model.instructor_id,
            start_at=db_model.start_at,
            end_at=db_model.end_at,
            reason=db_model.reason,
            is_recurring=db_model.is_recurring,
            recurrence_day=recurrence_day,
            created_at=db_model.created_at,
        )

    @staticmethod
    def to_orm(domain_entity: TimeOffEntity) -> TimeOffModel:
        """
        Convert domain entity to SQLAlchemy model (for creating new records).

        Args:
            domain_entity: The TimeOff domain entity

        Returns:
            SQLAlchemy TimeOff model
        """
        return TimeOffModel(
            id=domain_entity.id,
            instructor_id=domain_entity.instructor_id,
            start_at=domain_entity.start_at,
            end_at=domain_entity.end_at,
            reason=domain_entity.reason,
            is_recurring=domain_entity.is_recurring,
            recurrence_day=domain_entity.recurrence_day.value if domain_entity.recurrence_day else None,
        )

    @staticmethod
    def update_orm(db_model: TimeOffModel, domain_entity: TimeOffEntity) -> TimeOffModel:
        """
        Update SQLAlchemy model with values from domain entity.

        Args:
            db_model: The existing SQLAlchemy model
            domain_entity: The TimeOff domain entity with updated values

        Returns:
            Updated SQLAlchemy model
        """
        db_model.start_at = domain_entity.start_at
        db_model.end_at = domain_entity.end_at
        db_model.reason = domain_entity.reason
        db_model.is_recurring = domain_entity.is_recurring
        db_model.recurrence_day = domain_entity.recurrence_day.value if domain_entity.recurrence_day else None

        return db_model
