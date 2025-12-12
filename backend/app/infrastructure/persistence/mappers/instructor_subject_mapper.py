"""Mapper for InstructorSubject entity and SQLAlchemy InstructorSubject model."""

from typing import Dict, Any

from app.domains.subject.entities import InstructorSubject as DomainInstructorSubject
from app.infrastructure.persistence.sqlalchemy_models import (
    InstructorSubject as SQLAlchemyInstructorSubject,
    ProficiencyLevel,
)


class InstructorSubjectMapper:
    """
    Maps between domain InstructorSubject entity and SQLAlchemy InstructorSubject model.

    Note: Domain uses string IDs and has different structure than SQLAlchemy model.
    The SQLAlchemy model uses proficiency_level enum, while domain uses years_of_experience.
    """

    @staticmethod
    def to_domain(db_instructor_subject: SQLAlchemyInstructorSubject) -> DomainInstructorSubject:
        """
        Convert SQLAlchemy InstructorSubject to domain InstructorSubject entity.

        Args:
            db_instructor_subject: SQLAlchemy InstructorSubject model instance

        Returns:
            Domain InstructorSubject entity
        """
        if db_instructor_subject is None:
            return None

        # Map proficiency level to years of experience (rough approximation)
        years_map = {
            ProficiencyLevel.BEGINNER: 1.0,
            ProficiencyLevel.INTERMEDIATE: 3.0,
            ProficiencyLevel.EXPERT: 5.0,
            ProficiencyLevel.NATIVE: 10.0,
        }

        proficiency = db_instructor_subject.proficiency_level
        years = years_map.get(proficiency, 0.0)

        return DomainInstructorSubject(
            id=str(db_instructor_subject.id) if db_instructor_subject.id else None,
            instructor_id=str(db_instructor_subject.instructor_id),
            subject_id=str(db_instructor_subject.subject_id),
            years_of_experience=years,
            description=None,  # Not in SQLAlchemy model
            is_primary=False,  # Not in SQLAlchemy model
            created_at=db_instructor_subject.created_at,
            updated_at=db_instructor_subject.updated_at,
        )

    @staticmethod
    def to_persistence(domain_instructor_subject: DomainInstructorSubject) -> Dict[str, Any]:
        """
        Convert domain InstructorSubject entity to dict for SQLAlchemy update.

        Args:
            domain_instructor_subject: Domain InstructorSubject entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        # Map years of experience to proficiency level
        years = domain_instructor_subject.years_of_experience
        if years < 2.0:
            proficiency = ProficiencyLevel.BEGINNER
        elif years < 5.0:
            proficiency = ProficiencyLevel.INTERMEDIATE
        elif years < 10.0:
            proficiency = ProficiencyLevel.EXPERT
        else:
            proficiency = ProficiencyLevel.NATIVE

        return {
            "instructor_id": int(domain_instructor_subject.instructor_id),
            "subject_id": int(domain_instructor_subject.subject_id),
            "proficiency_level": proficiency,
        }

    @staticmethod
    def create_orm_instance(domain_instructor_subject: DomainInstructorSubject) -> SQLAlchemyInstructorSubject:
        """
        Create new SQLAlchemy InstructorSubject instance from domain InstructorSubject.

        Args:
            domain_instructor_subject: Domain InstructorSubject entity

        Returns:
            SQLAlchemy InstructorSubject model instance
        """
        # Map years of experience to proficiency level
        years = domain_instructor_subject.years_of_experience
        if years < 2.0:
            proficiency = ProficiencyLevel.BEGINNER
        elif years < 5.0:
            proficiency = ProficiencyLevel.INTERMEDIATE
        elif years < 10.0:
            proficiency = ProficiencyLevel.EXPERT
        else:
            proficiency = ProficiencyLevel.NATIVE

        return SQLAlchemyInstructorSubject(
            instructor_id=int(domain_instructor_subject.instructor_id),
            subject_id=int(domain_instructor_subject.subject_id),
            proficiency_level=proficiency,
        )

    @staticmethod
    def update_orm_instance(
        db_instructor_subject: SQLAlchemyInstructorSubject,
        domain_instructor_subject: DomainInstructorSubject
    ) -> None:
        """
        Update SQLAlchemy InstructorSubject instance from domain InstructorSubject.

        Args:
            db_instructor_subject: SQLAlchemy InstructorSubject model instance to update
            domain_instructor_subject: Domain InstructorSubject entity with new values
        """
        # Map years of experience to proficiency level
        years = domain_instructor_subject.years_of_experience
        if years < 2.0:
            proficiency = ProficiencyLevel.BEGINNER
        elif years < 5.0:
            proficiency = ProficiencyLevel.INTERMEDIATE
        elif years < 10.0:
            proficiency = ProficiencyLevel.EXPERT
        else:
            proficiency = ProficiencyLevel.NATIVE

        db_instructor_subject.proficiency_level = proficiency
