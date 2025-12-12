"""SQLAlchemy implementation of StudentProfile repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.student.entities import StudentProfile
from app.domains.student.repositories import IStudentProfileRepository
from app.infrastructure.persistence.mappers import StudentProfileMapper
from app.infrastructure.persistence.sqlalchemy_models import StudentProfile as SQLAlchemyStudentProfile


class SQLAlchemyStudentProfileRepository(IStudentProfileRepository):
    """
    SQLAlchemy implementation of IStudentProfileRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses StudentProfileMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = StudentProfileMapper

    def save(self, profile: StudentProfile) -> StudentProfile:
        """Save student profile to database."""
        try:
            db_profile = self.mapper.create_orm_instance(profile)
            self.db.add(db_profile)
            self.db.flush()

            profile.id = db_profile.id
            return profile

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save student profile: {str(e)}")

    def get_by_id(self, student_id: int) -> Optional[StudentProfile]:
        """Get student profile by ID."""
        try:
            db_profile = self.db.query(SQLAlchemyStudentProfile).filter(
                SQLAlchemyStudentProfile.id == student_id
            ).first()

            return self.mapper.to_domain(db_profile) if db_profile else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get student profile by ID: {str(e)}")

    def get_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        """Get student profile by user ID."""
        try:
            db_profile = self.db.query(SQLAlchemyStudentProfile).filter(
                SQLAlchemyStudentProfile.user_id == user_id
            ).first()

            return self.mapper.to_domain(db_profile) if db_profile else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get student profile by user ID: {str(e)}")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[StudentProfile]:
        """Get all student profiles."""
        try:
            db_profiles = self.db.query(SQLAlchemyStudentProfile).offset(skip).limit(limit).all()

            return [self.mapper.to_domain(db_profile) for db_profile in db_profiles]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get all student profiles: {str(e)}")

    def update(self, profile: StudentProfile) -> StudentProfile:
        """Update existing student profile."""
        try:
            db_profile = self.db.query(SQLAlchemyStudentProfile).filter(
                SQLAlchemyStudentProfile.id == profile.id
            ).first()

            if not db_profile:
                raise ValueError(f"Student profile with ID {profile.id} not found")

            self.mapper.update_orm_instance(db_profile, profile)
            self.db.flush()

            return profile

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update student profile: {str(e)}")

    def delete(self, student_id: int) -> bool:
        """Delete student profile."""
        try:
            db_profile = self.db.query(SQLAlchemyStudentProfile).filter(
                SQLAlchemyStudentProfile.id == student_id
            ).first()

            if not db_profile:
                return False

            self.db.delete(db_profile)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete student profile: {str(e)}")

    def count(self) -> int:
        """Count total student profiles."""
        try:
            return self.db.query(SQLAlchemyStudentProfile).count()

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count student profiles: {str(e)}")
