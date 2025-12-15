"""Mapper for ConversationReadStatus entity and SQLAlchemy model."""

from typing import Dict, Any
from app.domains.messaging.entities import ConversationReadStatus as DomainReadStatus
from app.database.models import ConversationReadStatus as SQLAlchemyReadStatus


class ReadStatusMapper:
    """
    Maps between domain ConversationReadStatus entity and SQLAlchemy model.
    """

    @staticmethod
    def to_domain(db_status: SQLAlchemyReadStatus) -> DomainReadStatus:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            db_status: SQLAlchemy model instance

        Returns:
            Domain entity
        """
        if db_status is None:
            return None

        return DomainReadStatus(
            id=db_status.id,
            conversation_id=db_status.conversation_id,
            user_id=db_status.user_id,
            last_read_message_id=db_status.last_read_message_id,
            last_read_at=db_status.last_read_at,
            created_at=db_status.created_at,
            updated_at=db_status.updated_at,
        )

    @staticmethod
    def create_orm_instance(domain_status: DomainReadStatus) -> SQLAlchemyReadStatus:
        """
        Create new SQLAlchemy instance from domain entity.

        Args:
            domain_status: Domain entity

        Returns:
            SQLAlchemy model instance
        """
        return SQLAlchemyReadStatus(
            conversation_id=domain_status.conversation_id,
            user_id=domain_status.user_id,
            last_read_message_id=domain_status.last_read_message_id,
            last_read_at=domain_status.last_read_at,
            created_at=domain_status.created_at,
            updated_at=domain_status.updated_at,
        )

    @staticmethod
    def update_orm_instance(
        db_status: SQLAlchemyReadStatus,
        domain_status: DomainReadStatus
    ) -> None:
        """
        Update SQLAlchemy instance from domain entity.

        Args:
            db_status: SQLAlchemy model instance to update
            domain_status: Domain entity with new values
        """
        db_status.last_read_message_id = domain_status.last_read_message_id
        db_status.last_read_at = domain_status.last_read_at
        db_status.updated_at = domain_status.updated_at
