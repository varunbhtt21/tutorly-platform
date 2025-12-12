"""SQLAlchemy implementation of Education repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.instructor.entities import Education
from app.domains.instructor.repositories import IEducationRepository
from app.infrastructure.persistence.mappers import EducationMapper
from app.infrastructure.persistence.sqlalchemy_models import Education as SQLAlchemyEducation


class SQLAlchemyEducationRepository(IEducationRepository):
    """
    SQLAlchemy implementation of IEducationRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses EducationMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = EducationMapper

    def save(self, education: Education) -> Education:
        """Save education record to database."""
        try:
            db_education = self.mapper.create_orm_instance(education)
            self.db.add(db_education)
            self.db.flush()

            education.id = db_education.id
            return education

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save education: {str(e)}")

    def get_by_id(self, education_id: int) -> Optional[Education]:
        """Get education record by ID."""
        try:
            db_education = self.db.query(SQLAlchemyEducation).filter(
                SQLAlchemyEducation.id == education_id
            ).first()

            return self.mapper.to_domain(db_education) if db_education else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get education by ID: {str(e)}")

    def get_by_instructor_id(self, instructor_id: int) -> List[Education]:
        """Get all education records for an instructor."""
        try:
            db_educations = self.db.query(SQLAlchemyEducation).filter(
                SQLAlchemyEducation.instructor_id == instructor_id
            ).all()

            return [self.mapper.to_domain(db_edu) for db_edu in db_educations]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get education by instructor ID: {str(e)}")

    def update(self, education: Education) -> Education:
        """Update existing education record."""
        try:
            db_education = self.db.query(SQLAlchemyEducation).filter(
                SQLAlchemyEducation.id == education.id
            ).first()

            if not db_education:
                raise ValueError(f"Education with ID {education.id} not found")

            self.mapper.update_orm_instance(db_education, education)
            self.db.flush()

            return education

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update education: {str(e)}")

    def delete(self, education_id: int) -> bool:
        """Delete education record."""
        try:
            db_education = self.db.query(SQLAlchemyEducation).filter(
                SQLAlchemyEducation.id == education_id
            ).first()

            if not db_education:
                return False

            self.db.delete(db_education)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete education: {str(e)}")
