"""SQLAlchemy implementation of Subject repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from app.domains.subject.entities import Subject
from app.domains.subject.repositories import ISubjectRepository
from app.infrastructure.persistence.mappers import SubjectMapper
from app.infrastructure.persistence.sqlalchemy_models import Subject as SQLAlchemySubject


class SQLAlchemySubjectRepository(ISubjectRepository):
    """
    SQLAlchemy implementation of ISubjectRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses SubjectMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = SubjectMapper

    def save(self, subject: Subject) -> Subject:
        """Save subject to database."""
        try:
            db_subject = self.mapper.create_orm_instance(subject)
            self.db.add(db_subject)
            self.db.flush()

            subject.id = str(db_subject.id)
            return subject

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save subject: {str(e)}")

    def get_by_id(self, subject_id: str) -> Optional[Subject]:
        """Get subject by ID."""
        try:
            db_subject = self.db.query(SQLAlchemySubject).filter(
                SQLAlchemySubject.id == int(subject_id)
            ).first()

            return self.mapper.to_domain(db_subject) if db_subject else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get subject by ID: {str(e)}")

    def get_by_name(self, name: str) -> Optional[Subject]:
        """Get subject by name (case-insensitive)."""
        try:
            db_subject = self.db.query(SQLAlchemySubject).filter(
                func.lower(SQLAlchemySubject.name) == name.lower()
            ).first()

            return self.mapper.to_domain(db_subject) if db_subject else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get subject by name: {str(e)}")

    def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Subject]:
        """Get subjects by category."""
        try:
            db_subjects = self.db.query(SQLAlchemySubject).filter(
                SQLAlchemySubject.category == category
            ).offset(skip).limit(limit).all()

            return [self.mapper.to_domain(db_subject) for db_subject in db_subjects]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get subjects by category: {str(e)}")

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> List[Subject]:
        """Get all subjects with optional filtering."""
        try:
            query = self.db.query(SQLAlchemySubject)

            if active_only:
                query = query.filter(SQLAlchemySubject.is_active == 1)

            db_subjects = query.offset(skip).limit(limit).all()

            return [self.mapper.to_domain(db_subject) for db_subject in db_subjects]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get all subjects: {str(e)}")

    def update(self, subject: Subject) -> Subject:
        """Update existing subject."""
        try:
            db_subject = self.db.query(SQLAlchemySubject).filter(
                SQLAlchemySubject.id == int(subject.id)
            ).first()

            if not db_subject:
                raise ValueError(f"Subject with ID {subject.id} not found")

            self.mapper.update_orm_instance(db_subject, subject)
            self.db.flush()

            return subject

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update subject: {str(e)}")

    def delete(self, subject_id: str) -> bool:
        """Delete subject."""
        try:
            db_subject = self.db.query(SQLAlchemySubject).filter(
                SQLAlchemySubject.id == int(subject_id)
            ).first()

            if not db_subject:
                return False

            self.db.delete(db_subject)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete subject: {str(e)}")

    def count(self, active_only: bool = False) -> int:
        """Count subjects with optional filtering."""
        try:
            query = self.db.query(SQLAlchemySubject)

            if active_only:
                query = query.filter(SQLAlchemySubject.is_active == 1)

            return query.count()

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count subjects: {str(e)}")
