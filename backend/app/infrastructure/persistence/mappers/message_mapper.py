"""Mapper for Message entity and SQLAlchemy model."""

from typing import Dict, Any
from app.domains.messaging.entities import Message as DomainMessage
from app.domains.messaging.value_objects import MessageType, MessageStatus
from app.database.models import Message as SQLAlchemyMessage


class MessageMapper:
    """
    Maps between domain Message entity and SQLAlchemy model.
    """

    @staticmethod
    def to_domain(db_message: SQLAlchemyMessage) -> DomainMessage:
        """
        Convert SQLAlchemy Message to domain entity.

        Args:
            db_message: SQLAlchemy model instance

        Returns:
            Domain Message entity
        """
        if db_message is None:
            return None

        return DomainMessage(
            id=db_message.id,
            conversation_id=db_message.conversation_id,
            sender_id=db_message.sender_id,
            content=db_message.content or "",
            message_type=MessageType(db_message.message_type.value),
            status=MessageStatus(db_message.status.value),
            reply_to_id=db_message.reply_to_id,
            created_at=db_message.created_at,
            updated_at=db_message.updated_at,
        )

    @staticmethod
    def to_persistence(domain_message: DomainMessage) -> Dict[str, Any]:
        """
        Convert domain entity to dict for SQLAlchemy update.

        Args:
            domain_message: Domain entity

        Returns:
            Dict of field values
        """
        return {
            "conversation_id": domain_message.conversation_id,
            "sender_id": domain_message.sender_id,
            "content": domain_message.content,
            "message_type": domain_message.message_type.value,
            "status": domain_message.status.value,
            "reply_to_id": domain_message.reply_to_id,
            "updated_at": domain_message.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_message: DomainMessage) -> SQLAlchemyMessage:
        """
        Create new SQLAlchemy instance from domain entity.

        Args:
            domain_message: Domain entity

        Returns:
            SQLAlchemy model instance
        """
        return SQLAlchemyMessage(
            conversation_id=domain_message.conversation_id,
            sender_id=domain_message.sender_id,
            content=domain_message.content,
            message_type=domain_message.message_type.value,
            status=domain_message.status.value,
            reply_to_id=domain_message.reply_to_id,
            created_at=domain_message.created_at,
            updated_at=domain_message.updated_at,
        )

    @staticmethod
    def update_orm_instance(
        db_message: SQLAlchemyMessage,
        domain_message: DomainMessage
    ) -> None:
        """
        Update SQLAlchemy instance from domain entity.

        Args:
            db_message: SQLAlchemy model instance to update
            domain_message: Domain entity with new values
        """
        db_message.content = domain_message.content
        db_message.status = domain_message.status.value
        db_message.updated_at = domain_message.updated_at
