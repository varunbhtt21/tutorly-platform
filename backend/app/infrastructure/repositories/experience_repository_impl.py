"""SQLAlchemy implementation of Experience repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.instructor.entities import Experience
from app.domains.instructor.repositories import IExperienceRepository
from app.infrastructure.persistence.mappers import ExperienceMapper
from app.infrastructure.persistence.sqlalchemy_models import Experience as SQLAlchemyExperience


class SQLAlchemyExperienceRepository(IExperienceRepository):
    """
    SQLAlchemy implementation of IExperienceRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses ExperienceMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = ExperienceMapper

    def save(self, experience: Experience) -> Experience:
        """Save experience record to database."""
        try:
            db_experience = self.mapper.create_orm_instance(experience)
            self.db.add(db_experience)
            self.db.flush()

            experience.id = db_experience.id
            return experience

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save experience: {str(e)}")

    def get_by_id(self, experience_id: int) -> Optional[Experience]:
        """Get experience record by ID."""
        try:
            db_experience = self.db.query(SQLAlchemyExperience).filter(
                SQLAlchemyExperience.id == experience_id
            ).first()

            return self.mapper.to_domain(db_experience) if db_experience else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get experience by ID: {str(e)}")

    def get_by_instructor_id(self, instructor_id: int) -> List[Experience]:
        """Get all experience records for an instructor."""
        try:
            db_experiences = self.db.query(SQLAlchemyExperience).filter(
                SQLAlchemyExperience.instructor_id == instructor_id
            ).all()

            return [self.mapper.to_domain(db_exp) for db_exp in db_experiences]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get experience by instructor ID: {str(e)}")

    def update(self, experience: Experience) -> Experience:
        """Update existing experience record."""
        try:
            db_experience = self.db.query(SQLAlchemyExperience).filter(
                SQLAlchemyExperience.id == experience.id
            ).first()

            if not db_experience:
                raise ValueError(f"Experience with ID {experience.id} not found")

            self.mapper.update_orm_instance(db_experience, experience)
            self.db.flush()

            return experience

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update experience: {str(e)}")

    def delete(self, experience_id: int) -> bool:
        """Delete experience record."""
        try:
            db_experience = self.db.query(SQLAlchemyExperience).filter(
                SQLAlchemyExperience.id == experience_id
            ).first()

            if not db_experience:
                return False

            self.db.delete(db_experience)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete experience: {str(e)}")
