"""Mapper for StudentProfile entity and SQLAlchemy StudentProfile model."""

from typing import Dict, Any, Optional

from app.domains.student.entities import StudentProfile as DomainStudentProfile
from app.infrastructure.persistence.sqlalchemy_models import StudentProfile as SQLAlchemyStudentProfile


class StudentProfileMapper:
    """
    Maps between domain StudentProfile entity and SQLAlchemy StudentProfile model.
    """

    @staticmethod
    def to_domain(db_student: SQLAlchemyStudentProfile) -> DomainStudentProfile:
        """
        Convert SQLAlchemy StudentProfile to domain StudentProfile entity.

        Args:
            db_student: SQLAlchemy StudentProfile model instance

        Returns:
            Domain StudentProfile entity
        """
        if db_student is None:
            return None

        return DomainStudentProfile(
            id=db_student.id,
            user_id=db_student.user_id,
            profile_photo_url=db_student.profile_photo_url,
            learning_goals=db_student.learning_goals,
            preferred_language=db_student.preferred_language,
            notification_preferences=db_student.notification_preferences,
            preferred_session_duration=db_student.preferred_session_duration,
            total_sessions_completed=db_student.total_sessions_completed,
            total_spent=db_student.total_spent,
            created_at=db_student.created_at,
            updated_at=db_student.updated_at,
        )

    @staticmethod
    def to_persistence(domain_student: DomainStudentProfile) -> Dict[str, Any]:
        """
        Convert domain StudentProfile entity to dict for SQLAlchemy update.

        Args:
            domain_student: Domain StudentProfile entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        return {
            "user_id": domain_student.user_id,
            "profile_photo_url": domain_student.profile_photo_url,
            "learning_goals": domain_student.learning_goals,
            "preferred_language": domain_student.preferred_language,
            "notification_preferences": domain_student.notification_preferences,
            "preferred_session_duration": domain_student.preferred_session_duration,
            "total_sessions_completed": domain_student.total_sessions_completed,
            "total_spent": domain_student.total_spent,
            "updated_at": domain_student.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_student: DomainStudentProfile) -> SQLAlchemyStudentProfile:
        """
        Create new SQLAlchemy StudentProfile instance from domain StudentProfile.

        Args:
            domain_student: Domain StudentProfile entity

        Returns:
            SQLAlchemy StudentProfile model instance
        """
        return SQLAlchemyStudentProfile(
            user_id=domain_student.user_id,
            profile_photo_url=domain_student.profile_photo_url,
            learning_goals=domain_student.learning_goals,
            preferred_language=domain_student.preferred_language,
            notification_preferences=domain_student.notification_preferences,
            preferred_session_duration=domain_student.preferred_session_duration,
            total_sessions_completed=domain_student.total_sessions_completed,
            total_spent=domain_student.total_spent,
        )

    @staticmethod
    def update_orm_instance(
        db_student: SQLAlchemyStudentProfile,
        domain_student: DomainStudentProfile
    ) -> None:
        """
        Update SQLAlchemy StudentProfile instance from domain StudentProfile.

        Args:
            db_student: SQLAlchemy StudentProfile model instance to update
            domain_student: Domain StudentProfile entity with new values
        """
        db_student.profile_photo_url = domain_student.profile_photo_url
        db_student.learning_goals = domain_student.learning_goals
        db_student.preferred_language = domain_student.preferred_language
        db_student.notification_preferences = domain_student.notification_preferences
        db_student.preferred_session_duration = domain_student.preferred_session_duration
        db_student.total_sessions_completed = domain_student.total_sessions_completed
        db_student.total_spent = domain_student.total_spent
        db_student.updated_at = domain_student.updated_at
