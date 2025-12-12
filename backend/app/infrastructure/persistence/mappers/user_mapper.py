"""Mapper for User entity and SQLAlchemy User model."""

from typing import Dict, Any, Optional
from app.domains.user.entities import User as DomainUser
from app.domains.user.value_objects import Email, Password, UserRole, UserStatus
from app.infrastructure.persistence.sqlalchemy_models import User as SQLAlchemyUser


class UserMapper:
    """
    Maps between domain User entity and SQLAlchemy User model.

    Converts value objects to primitives and vice versa.
    """

    @staticmethod
    def to_domain(db_user: SQLAlchemyUser) -> DomainUser:
        """
        Convert SQLAlchemy User to domain User entity.

        Args:
            db_user: SQLAlchemy User model instance

        Returns:
            Domain User entity
        """
        if db_user is None:
            return None

        return DomainUser(
            id=db_user.id,
            email=Email(value=db_user.email),
            password=Password.create_from_hash(db_user.hashed_password),
            role=UserRole(db_user.role.value),
            status=UserStatus(db_user.status.value),
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            phone_number=db_user.phone_number,
            email_verified=db_user.is_email_verified,
            terms_accepted=True,  # Assumed if user exists
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login_at=db_user.last_login_at,
            email_verified_at=db_user.updated_at if db_user.is_email_verified else None,
        )

    @staticmethod
    def to_persistence(domain_user: DomainUser) -> Dict[str, Any]:
        """
        Convert domain User entity to dict for SQLAlchemy update.

        Args:
            domain_user: Domain User entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        return {
            "email": str(domain_user.email),
            "hashed_password": domain_user.password.hashed_value,
            "role": domain_user.role.value,
            "status": domain_user.status.value,
            "first_name": domain_user.first_name,
            "last_name": domain_user.last_name,
            "phone_number": domain_user.phone_number,
            "is_email_verified": domain_user.email_verified,
            "last_login_at": domain_user.last_login_at,
            "created_at": domain_user.created_at,
            "updated_at": domain_user.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_user: DomainUser) -> SQLAlchemyUser:
        """
        Create new SQLAlchemy User instance from domain User.

        Args:
            domain_user: Domain User entity

        Returns:
            SQLAlchemy User model instance
        """
        return SQLAlchemyUser(
            email=str(domain_user.email),
            hashed_password=domain_user.password.hashed_value,
            role=domain_user.role.value,
            status=domain_user.status.value,
            first_name=domain_user.first_name,
            last_name=domain_user.last_name,
            phone_number=domain_user.phone_number,
            is_email_verified=domain_user.email_verified,
            last_login_at=domain_user.last_login_at,
        )

    @staticmethod
    def update_orm_instance(db_user: SQLAlchemyUser, domain_user: DomainUser) -> None:
        """
        Update SQLAlchemy User instance from domain User.

        Args:
            db_user: SQLAlchemy User model instance to update
            domain_user: Domain User entity with new values
        """
        db_user.email = str(domain_user.email)
        db_user.hashed_password = domain_user.password.hashed_value
        db_user.role = domain_user.role.value
        db_user.status = domain_user.status.value
        db_user.first_name = domain_user.first_name
        db_user.last_name = domain_user.last_name
        db_user.phone_number = domain_user.phone_number
        db_user.is_email_verified = domain_user.email_verified
        db_user.last_login_at = domain_user.last_login_at
        db_user.updated_at = domain_user.updated_at
