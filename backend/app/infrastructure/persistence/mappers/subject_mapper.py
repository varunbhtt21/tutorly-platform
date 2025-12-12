"""Mapper for Subject entity and SQLAlchemy Subject model."""

from typing import Dict, Any

from app.domains.subject.entities import Subject as DomainSubject
from app.infrastructure.persistence.sqlalchemy_models import Subject as SQLAlchemySubject


class SubjectMapper:
    """
    Maps between domain Subject entity and SQLAlchemy Subject model.

    Note: Domain Subject uses string ID, while SQLAlchemy model uses integer ID.
    Conversion happens during mapping.
    """

    @staticmethod
    def to_domain(db_subject: SQLAlchemySubject) -> DomainSubject:
        """
        Convert SQLAlchemy Subject to domain Subject entity.

        Args:
            db_subject: SQLAlchemy Subject model instance

        Returns:
            Domain Subject entity
        """
        if db_subject is None:
            return None

        return DomainSubject(
            id=str(db_subject.id) if db_subject.id else None,
            name=db_subject.name,
            category=db_subject.category.value if hasattr(db_subject.category, 'value') else db_subject.category,
            description=db_subject.description,
            icon_url=None,  # Not in current SQLAlchemy model
            is_active=bool(db_subject.is_active),
            total_instructors=0,  # Calculated separately or from join count
            created_at=db_subject.created_at,
            updated_at=db_subject.updated_at,
        )

    @staticmethod
    def to_persistence(domain_subject: DomainSubject) -> Dict[str, Any]:
        """
        Convert domain Subject entity to dict for SQLAlchemy update.

        Args:
            domain_subject: Domain Subject entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        return {
            "name": domain_subject.name,
            "category": domain_subject.category,
            "description": domain_subject.description,
            "is_active": 1 if domain_subject.is_active else 0,
        }

    @staticmethod
    def create_orm_instance(domain_subject: DomainSubject) -> SQLAlchemySubject:
        """
        Create new SQLAlchemy Subject instance from domain Subject.

        Args:
            domain_subject: Domain Subject entity

        Returns:
            SQLAlchemy Subject model instance
        """
        return SQLAlchemySubject(
            name=domain_subject.name,
            category=domain_subject.category,
            description=domain_subject.description,
            is_active=1 if domain_subject.is_active else 0,
        )

    @staticmethod
    def update_orm_instance(
        db_subject: SQLAlchemySubject,
        domain_subject: DomainSubject
    ) -> None:
        """
        Update SQLAlchemy Subject instance from domain Subject.

        Args:
            db_subject: SQLAlchemy Subject model instance to update
            domain_subject: Domain Subject entity with new values
        """
        db_subject.name = domain_subject.name
        db_subject.category = domain_subject.category
        db_subject.description = domain_subject.description
        db_subject.is_active = 1 if domain_subject.is_active else 0
