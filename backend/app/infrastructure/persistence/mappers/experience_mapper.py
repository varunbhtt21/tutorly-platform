"""Mapper for Experience entity and SQLAlchemy Experience model."""

from typing import Dict, Any

from app.domains.instructor.entities import Experience as DomainExperience
from app.infrastructure.persistence.sqlalchemy_models import Experience as SQLAlchemyExperience


class ExperienceMapper:
    """
    Maps between domain Experience entity and SQLAlchemy Experience model.

    Translates between database schema (company, start_year/end_year)
    and domain model (company_name, start_date/end_date).
    """

    @staticmethod
    def to_domain(db_experience: SQLAlchemyExperience) -> DomainExperience:
        """
        Convert SQLAlchemy Experience to domain Experience entity.

        Translates database schema to domain model:
        - instructor_profile_id → instructor_id
        - company → company_name
        - start_year/end_year → start_date/end_date (YYYY-MM format)

        Args:
            db_experience: SQLAlchemy Experience model instance

        Returns:
            Domain Experience entity
        """
        if db_experience is None:
            return None

        # Convert year integers to YYYY-MM date strings
        start_date = f"{db_experience.start_year}-01" if db_experience.start_year else None
        end_date = f"{db_experience.end_year}-12" if db_experience.end_year else None

        return DomainExperience(
            id=db_experience.id,
            instructor_id=db_experience.instructor_profile_id,  # Map profile_id to instructor_id
            company_name=db_experience.company,  # Map company to company_name
            position=db_experience.position,
            start_date=start_date,  # Convert year to date string
            end_date=end_date,  # Convert year to date string
            description=db_experience.description,
            is_current=db_experience.is_current,
            created_at=db_experience.created_at,
            updated_at=db_experience.updated_at,
        )

    @staticmethod
    def to_persistence(domain_experience: DomainExperience) -> Dict[str, Any]:
        """
        Convert domain Experience entity to dict for SQLAlchemy update.

        Translates domain model to database schema:
        - instructor_id → instructor_profile_id
        - company_name → company
        - start_date/end_date (YYYY-MM) → start_year/end_year

        Args:
            domain_experience: Domain Experience entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        # Extract years from YYYY-MM date strings
        start_year = int(domain_experience.start_date.split('-')[0]) if domain_experience.start_date else None
        end_year = int(domain_experience.end_date.split('-')[0]) if domain_experience.end_date and domain_experience.end_date != "Present" else None

        return {
            "instructor_profile_id": domain_experience.instructor_id,  # Map instructor_id to profile_id
            "company": domain_experience.company_name,  # Map company_name to company
            "position": domain_experience.position,
            "start_year": start_year,  # Convert date string to year
            "end_year": end_year,  # Convert date string to year
            "description": domain_experience.description,
            "is_current": domain_experience.is_current,
            "updated_at": domain_experience.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_experience: DomainExperience) -> SQLAlchemyExperience:
        """
        Create new SQLAlchemy Experience instance from domain Experience.

        Translates domain model to database schema:
        - instructor_id → instructor_profile_id
        - company_name → company
        - start_date/end_date (YYYY-MM) → start_year/end_year

        Args:
            domain_experience: Domain Experience entity

        Returns:
            SQLAlchemy Experience model instance
        """
        # Extract years from YYYY-MM date strings
        start_year = int(domain_experience.start_date.split('-')[0]) if domain_experience.start_date else None
        end_year = int(domain_experience.end_date.split('-')[0]) if domain_experience.end_date and domain_experience.end_date != "Present" else None

        return SQLAlchemyExperience(
            instructor_profile_id=domain_experience.instructor_id,  # Map instructor_id to profile_id
            company=domain_experience.company_name,  # Map company_name to company
            position=domain_experience.position,
            start_year=start_year,  # Convert date string to year
            end_year=end_year,  # Convert date string to year
            description=domain_experience.description,
            is_current=domain_experience.is_current,
        )

    @staticmethod
    def update_orm_instance(
        db_experience: SQLAlchemyExperience,
        domain_experience: DomainExperience
    ) -> None:
        """
        Update SQLAlchemy Experience instance from domain Experience.

        Translates domain model to database schema for updates.

        Args:
            db_experience: SQLAlchemy Experience model instance to update
            domain_experience: Domain Experience entity with new values
        """
        # Extract years from YYYY-MM date strings
        start_year = int(domain_experience.start_date.split('-')[0]) if domain_experience.start_date else None
        end_year = int(domain_experience.end_date.split('-')[0]) if domain_experience.end_date and domain_experience.end_date != "Present" else None

        db_experience.company = domain_experience.company_name  # Map company_name to company
        db_experience.position = domain_experience.position
        db_experience.start_year = start_year  # Convert date string to year
        db_experience.end_year = end_year  # Convert date string to year
        db_experience.description = domain_experience.description
        db_experience.is_current = domain_experience.is_current
        db_experience.updated_at = domain_experience.updated_at
