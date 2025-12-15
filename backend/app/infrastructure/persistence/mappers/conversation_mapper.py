"""Mapper for Conversation entity and SQLAlchemy model."""

from typing import Dict, Any
from app.domains.messaging.entities import Conversation as DomainConversation
from app.database.models import Conversation as SQLAlchemyConversation


class ConversationMapper:
    """
    Maps between domain Conversation entity and SQLAlchemy model.
    """

    @staticmethod
    def to_domain(db_conversation: SQLAlchemyConversation) -> DomainConversation:
        """
        Convert SQLAlchemy Conversation to domain entity.

        Args:
            db_conversation: SQLAlchemy model instance

        Returns:
            Domain Conversation entity
        """
        if db_conversation is None:
            return None

        return DomainConversation(
            id=db_conversation.id,
            participant_1_id=db_conversation.participant_1_id,
            participant_2_id=db_conversation.participant_2_id,
            last_message_id=db_conversation.last_message_id,
            last_message_at=db_conversation.last_message_at,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
        )

    @staticmethod
    def to_persistence(domain_conversation: DomainConversation) -> Dict[str, Any]:
        """
        Convert domain entity to dict for SQLAlchemy update.

        Args:
            domain_conversation: Domain entity

        Returns:
            Dict of field values
        """
        return {
            "participant_1_id": domain_conversation.participant_1_id,
            "participant_2_id": domain_conversation.participant_2_id,
            "last_message_id": domain_conversation.last_message_id,
            "last_message_at": domain_conversation.last_message_at,
            "updated_at": domain_conversation.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_conversation: DomainConversation) -> SQLAlchemyConversation:
        """
        Create new SQLAlchemy instance from domain entity.

        Args:
            domain_conversation: Domain entity

        Returns:
            SQLAlchemy model instance
        """
        return SQLAlchemyConversation(
            participant_1_id=domain_conversation.participant_1_id,
            participant_2_id=domain_conversation.participant_2_id,
            last_message_id=domain_conversation.last_message_id,
            last_message_at=domain_conversation.last_message_at,
            created_at=domain_conversation.created_at,
            updated_at=domain_conversation.updated_at,
        )

    @staticmethod
    def update_orm_instance(
        db_conversation: SQLAlchemyConversation,
        domain_conversation: DomainConversation
    ) -> None:
        """
        Update SQLAlchemy instance from domain entity.

        Args:
            db_conversation: SQLAlchemy model instance to update
            domain_conversation: Domain entity with new values
        """
        db_conversation.last_message_id = domain_conversation.last_message_id
        db_conversation.last_message_at = domain_conversation.last_message_at
        db_conversation.updated_at = domain_conversation.updated_at
