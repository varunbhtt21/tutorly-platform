"""SQLAlchemy implementation of InstructorSubject repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.subject.entities import InstructorSubject
from app.domains.subject.repositories import IInstructorSubjectRepository
from app.infrastructure.persistence.mappers import InstructorSubjectMapper
from app.infrastructure.persistence.sqlalchemy_models import InstructorSubject as SQLAlchemyInstructorSubject


class SQLAlchemyInstructorSubjectRepository(IInstructorSubjectRepository):
    """
    SQLAlchemy implementation of IInstructorSubjectRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses InstructorSubjectMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = InstructorSubjectMapper

    def save(self, instructor_subject: InstructorSubject) -> InstructorSubject:
        """Save instructor-subject relationship to database."""
        try:
            db_instructor_subject = self.mapper.create_orm_instance(instructor_subject)
            self.db.add(db_instructor_subject)
            self.db.flush()

            instructor_subject.id = str(db_instructor_subject.id)
            return instructor_subject

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save instructor-subject: {str(e)}")

    def get_by_id(self, instructor_subject_id: str) -> Optional[InstructorSubject]:
        """Get instructor-subject by ID."""
        try:
            db_instructor_subject = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.id == int(instructor_subject_id)
            ).first()

            return self.mapper.to_domain(db_instructor_subject) if db_instructor_subject else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get instructor-subject by ID: {str(e)}")

    def get_by_instructor(self, instructor_id: str) -> List[InstructorSubject]:
        """Get all subjects taught by an instructor."""
        try:
            db_instructor_subjects = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.instructor_id == int(instructor_id)
            ).all()

            return [self.mapper.to_domain(db_is) for db_is in db_instructor_subjects]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get subjects by instructor: {str(e)}")

    def get_by_subject(self, subject_id: str) -> List[InstructorSubject]:
        """Get all instructors teaching a subject."""
        try:
            db_instructor_subjects = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.subject_id == int(subject_id)
            ).all()

            return [self.mapper.to_domain(db_is) for db_is in db_instructor_subjects]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get instructors by subject: {str(e)}")

    def get_by_instructor_and_subject(
        self,
        instructor_id: str,
        subject_id: str,
    ) -> Optional[InstructorSubject]:
        """Get specific instructor-subject relationship."""
        try:
            db_instructor_subject = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.instructor_id == int(instructor_id),
                SQLAlchemyInstructorSubject.subject_id == int(subject_id)
            ).first()

            return self.mapper.to_domain(db_instructor_subject) if db_instructor_subject else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get instructor-subject relationship: {str(e)}")

    def update(self, instructor_subject: InstructorSubject) -> InstructorSubject:
        """Update existing instructor-subject relationship."""
        try:
            db_instructor_subject = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.id == int(instructor_subject.id)
            ).first()

            if not db_instructor_subject:
                raise ValueError(f"InstructorSubject with ID {instructor_subject.id} not found")

            self.mapper.update_orm_instance(db_instructor_subject, instructor_subject)
            self.db.flush()

            return instructor_subject

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update instructor-subject: {str(e)}")

    def delete(self, instructor_subject_id: str) -> bool:
        """Delete instructor-subject relationship."""
        try:
            db_instructor_subject = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.id == int(instructor_subject_id)
            ).first()

            if not db_instructor_subject:
                return False

            self.db.delete(db_instructor_subject)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete instructor-subject: {str(e)}")

    def exists(self, instructor_id: str, subject_id: str) -> bool:
        """Check if instructor-subject relationship exists."""
        try:
            count = self.db.query(SQLAlchemyInstructorSubject).filter(
                SQLAlchemyInstructorSubject.instructor_id == int(instructor_id),
                SQLAlchemyInstructorSubject.subject_id == int(subject_id)
            ).count()

            return count > 0

        except SQLAlchemyError as e:
            raise Exception(f"Failed to check instructor-subject existence: {str(e)}")
