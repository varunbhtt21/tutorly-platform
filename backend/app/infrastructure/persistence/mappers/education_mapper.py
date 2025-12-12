"""Mapper for Education entity and SQLAlchemy Education model."""

from typing import Dict, Any

from app.domains.instructor.entities import Education as DomainEducation
from app.infrastructure.persistence.sqlalchemy_models import Education as SQLAlchemyEducation


class EducationMapper:
    """
    Maps between domain Education entity and SQLAlchemy Education model.

    Simple mapping - no complex value objects.
    """

    @staticmethod
    def to_domain(db_education: SQLAlchemyEducation) -> DomainEducation:
        """
        Convert SQLAlchemy Education to domain Education entity.

        Translates database schema to domain model:
        - instructor_profile_id → instructor_id
        - institution → institution_name
        - end_year (or start_year) → year_of_graduation

        Args:
            db_education: SQLAlchemy Education model instance

        Returns:
            Domain Education entity
        """
        if db_education is None:
            return None

        return DomainEducation(
            id=db_education.id,
            instructor_id=db_education.instructor_profile_id,  # Map profile_id to instructor_id
            institution_name=db_education.institution,  # Map institution to institution_name
            degree=db_education.degree,
            field_of_study=db_education.field_of_study,
            year_of_graduation=db_education.end_year or db_education.start_year,  # Map end_year to year_of_graduation
            certificate_url=None,  # Database has no certificate_url field
            is_verified=False,  # Database has no is_verified field
            created_at=db_education.created_at,
            updated_at=db_education.updated_at,
        )

    @staticmethod
    def to_persistence(domain_education: DomainEducation) -> Dict[str, Any]:
        """
        Convert domain Education entity to dict for SQLAlchemy update.

        Translates domain model to database schema:
        - instructor_id → instructor_profile_id
        - institution_name → institution
        - year_of_graduation → end_year and start_year

        Args:
            domain_education: Domain Education entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        return {
            "instructor_profile_id": domain_education.instructor_id,  # Map instructor_id to profile_id
            "institution": domain_education.institution_name,  # Map institution_name to institution
            "degree": domain_education.degree,
            "field_of_study": domain_education.field_of_study,
            "start_year": domain_education.year_of_graduation,  # Use year_of_graduation as both start and end
            "end_year": domain_education.year_of_graduation,
            "is_current": False,  # Assuming completed education
            "description": None,  # Domain doesn't have description
            "updated_at": domain_education.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_education: DomainEducation) -> SQLAlchemyEducation:
        """
        Create new SQLAlchemy Education instance from domain Education.

        Translates domain model to database schema:
        - instructor_id → instructor_profile_id
        - institution_name → institution
        - year_of_graduation → start_year and end_year

        Args:
            domain_education: Domain Education entity

        Returns:
            SQLAlchemy Education model instance
        """
        return SQLAlchemyEducation(
            instructor_profile_id=domain_education.instructor_id,  # Map instructor_id to profile_id
            institution=domain_education.institution_name,  # Map institution_name to institution
            degree=domain_education.degree,
            field_of_study=domain_education.field_of_study,
            start_year=domain_education.year_of_graduation,  # Use year_of_graduation as both
            end_year=domain_education.year_of_graduation,
            is_current=False,  # Assuming completed education
            description=None,  # Domain doesn't have description
        )

    @staticmethod
    def update_orm_instance(
        db_education: SQLAlchemyEducation,
        domain_education: DomainEducation
    ) -> None:
        """
        Update SQLAlchemy Education instance from domain Education.

        Translates domain model to database schema for updates.

        Args:
            db_education: SQLAlchemy Education model instance to update
            domain_education: Domain Education entity with new values
        """
        db_education.institution = domain_education.institution_name  # Map institution_name to institution
        db_education.degree = domain_education.degree
        db_education.field_of_study = domain_education.field_of_study
        db_education.start_year = domain_education.year_of_graduation  # Map to both start and end
        db_education.end_year = domain_education.year_of_graduation
        db_education.updated_at = domain_education.updated_at
