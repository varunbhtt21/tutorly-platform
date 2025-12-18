"""SQLAlchemy implementation of InstructorProfile repository."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.value_objects import InstructorStatus
from app.domains.instructor.repositories import IInstructorProfileRepository
from app.domains.user.entities import User
from app.infrastructure.persistence.mappers import InstructorProfileMapper, UserMapper
from app.infrastructure.persistence.sqlalchemy_models import (
    InstructorProfile as SQLAlchemyInstructorProfile,
    User as SQLAlchemyUser,
)


class SQLAlchemyInstructorProfileRepository(IInstructorProfileRepository):
    """
    SQLAlchemy implementation of IInstructorProfileRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses InstructorProfileMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = InstructorProfileMapper

    def save(self, profile: InstructorProfile) -> InstructorProfile:
        """Save instructor profile to database."""
        try:
            db_profile = self.mapper.create_orm_instance(profile)
            self.db.add(db_profile)
            self.db.flush()

            profile.id = db_profile.id
            return profile

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save instructor profile: {str(e)}")

    def get_by_id(self, instructor_id: int) -> Optional[InstructorProfile]:
        """Get instructor profile by ID."""
        try:
            db_profile = self.db.query(SQLAlchemyInstructorProfile).filter(
                SQLAlchemyInstructorProfile.id == instructor_id
            ).first()

            return self.mapper.to_domain(db_profile) if db_profile else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get instructor profile by ID: {str(e)}")

    def get_by_user_id(self, user_id: int) -> Optional[InstructorProfile]:
        """Get instructor profile by user ID."""
        try:
            db_profile = self.db.query(SQLAlchemyInstructorProfile).filter(
                SQLAlchemyInstructorProfile.user_id == user_id
            ).first()

            return self.mapper.to_domain(db_profile) if db_profile else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get instructor profile by user ID: {str(e)}")

    def get_all(
        self,
        status: Optional[InstructorStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InstructorProfile]:
        """Get all instructor profiles with optional filtering."""
        try:
            query = self.db.query(SQLAlchemyInstructorProfile)

            if status:
                query = query.filter(SQLAlchemyInstructorProfile.status == status.value)

            db_profiles = query.offset(skip).limit(limit).all()

            return [self.mapper.to_domain(db_profile) for db_profile in db_profiles]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get all instructor profiles: {str(e)}")

    def update(self, profile: InstructorProfile) -> InstructorProfile:
        """Update existing instructor profile."""
        try:
            db_profile = self.db.query(SQLAlchemyInstructorProfile).filter(
                SQLAlchemyInstructorProfile.id == profile.id
            ).first()

            if not db_profile:
                raise ValueError(f"Instructor profile with ID {profile.id} not found")

            self.mapper.update_orm_instance(db_profile, profile)
            self.db.flush()

            return profile

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update instructor profile: {str(e)}")

    def delete(self, instructor_id: int) -> bool:
        """Delete instructor profile."""
        try:
            db_profile = self.db.query(SQLAlchemyInstructorProfile).filter(
                SQLAlchemyInstructorProfile.id == instructor_id
            ).first()

            if not db_profile:
                return False

            self.db.delete(db_profile)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete instructor profile: {str(e)}")

    def count(self, status: Optional[InstructorStatus] = None) -> int:
        """Count instructor profiles with optional filtering."""
        try:
            query = self.db.query(SQLAlchemyInstructorProfile)

            if status:
                query = query.filter(SQLAlchemyInstructorProfile.status == status.value)

            return query.count()

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count instructor profiles: {str(e)}")

    def get_dashboard_data(self, user_id: int) -> Optional[Tuple[InstructorProfile, User]]:
        """
        Get instructor profile with user data for dashboard.

        Optimized query for dashboard display - retrieves both profile
        and user data in efficient queries.
        """
        try:
            # Get instructor profile
            db_profile = self.db.query(SQLAlchemyInstructorProfile).filter(
                SQLAlchemyInstructorProfile.user_id == user_id
            ).first()

            if not db_profile:
                return None

            # Get user data
            db_user = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.id == user_id
            ).first()

            if not db_user:
                return None

            # Map to domain entities
            profile = self.mapper.to_domain(db_profile)
            user = UserMapper.to_domain(db_user)

            return (profile, user)

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get dashboard data: {str(e)}")

    def get_with_user(self, instructor_id: int) -> Optional[Tuple[InstructorProfile, User]]:
        """
        Get instructor profile with user data by profile ID.

        Retrieves both the instructor profile and user entity for use cases
        that need instructor details (name, email) along with profile data.
        """
        try:
            # Get instructor profile by profile ID
            db_profile = self.db.query(SQLAlchemyInstructorProfile).filter(
                SQLAlchemyInstructorProfile.id == instructor_id
            ).first()

            if not db_profile:
                return None

            # Get user data using profile's user_id
            db_user = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.id == db_profile.user_id
            ).first()

            if not db_user:
                return None

            # Map to domain entities
            profile = self.mapper.to_domain(db_profile)
            user = UserMapper.to_domain(db_user)

            return (profile, user)

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get instructor with user: {str(e)}")
