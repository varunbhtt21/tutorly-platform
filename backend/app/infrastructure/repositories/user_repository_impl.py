"""SQLAlchemy implementation of User repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.user.entities import User
from app.domains.user.value_objects import Email, UserRole, UserStatus
from app.domains.user.repositories import IUserRepository
from app.infrastructure.persistence.mappers import UserMapper
from app.infrastructure.persistence.sqlalchemy_models import User as SQLAlchemyUser


class SQLAlchemyUserRepository(IUserRepository):
    """
    SQLAlchemy implementation of IUserRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    Uses UserMapper to convert between domain and ORM models.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = UserMapper

    def save(self, user: User) -> User:
        """
        Save user to database.
        If user has an ID, updates existing record.
        If user has no ID, creates new record.

        Args:
            user: User entity

        Returns:
            Saved user with ID
        """
        try:
            # Check if this is an existing user (has ID) or new user (no ID)
            if user.id is not None:
                # Existing user - update it
                return self.update(user)
            else:
                # New user - create it
                db_user = self.mapper.create_orm_instance(user)

                # Add to session and flush to get ID
                self.db.add(db_user)
                self.db.flush()

                # Convert back to domain entity with ID
                user.id = db_user.id

                return user

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save user: {str(e)}")

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        try:
            db_user = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.id == user_id,
                SQLAlchemyUser.deleted_at.is_(None)  # Soft delete check
            ).first()

            return self.mapper.to_domain(db_user) if db_user else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get user by ID: {str(e)}")

    def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        try:
            db_user = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.email == str(email),
                SQLAlchemyUser.deleted_at.is_(None)
            ).first()

            return self.mapper.to_domain(db_user) if db_user else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get user by email: {str(e)}")

    def email_exists(self, email: Email) -> bool:
        """
        Check if email exists.

        Args:
            email: Email to check

        Returns:
            True if exists, False otherwise
        """
        try:
            count = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.email == str(email),
                SQLAlchemyUser.deleted_at.is_(None)
            ).count()

            return count > 0

        except SQLAlchemyError as e:
            raise Exception(f"Failed to check email existence: {str(e)}")

    def get_all(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Get all users with optional filtering.

        Args:
            role: Filter by role
            status: Filter by status
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of users
        """
        try:
            query = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.deleted_at.is_(None)
            )

            # Apply filters
            if role:
                query = query.filter(SQLAlchemyUser.role == role.value)

            if status:
                query = query.filter(SQLAlchemyUser.status == status.value)

            # Pagination
            db_users = query.offset(skip).limit(limit).all()

            return [self.mapper.to_domain(db_user) for db_user in db_users]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get all users: {str(e)}")

    def update(self, user: User) -> User:
        """
        Update existing user.

        Args:
            user: User entity with changes

        Returns:
            Updated user
        """
        try:
            # Get existing user
            db_user = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.id == user.id
            ).first()

            if not db_user:
                raise ValueError(f"User with ID {user.id} not found")

            # Update ORM instance from domain entity
            self.mapper.update_orm_instance(db_user, user)

            # Flush changes
            self.db.flush()

            return user

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update user: {str(e)}")

    def delete(self, user_id: int) -> bool:
        """
        Delete user (hard delete).

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        try:
            db_user = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.id == user_id
            ).first()

            if not db_user:
                return False

            self.db.delete(db_user)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete user: {str(e)}")

    def count(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
    ) -> int:
        """
        Count users with optional filtering.

        Args:
            role: Filter by role
            status: Filter by status

        Returns:
            Number of users
        """
        try:
            query = self.db.query(SQLAlchemyUser).filter(
                SQLAlchemyUser.deleted_at.is_(None)
            )

            # Apply filters
            if role:
                query = query.filter(SQLAlchemyUser.role == role.value)

            if status:
                query = query.filter(SQLAlchemyUser.status == status.value)

            return query.count()

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count users: {str(e)}")
