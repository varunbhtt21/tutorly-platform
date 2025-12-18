"""SQLAlchemy implementation of Message repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, and_, or_, func

from app.domains.messaging.entities import Message
from app.domains.messaging.value_objects import MessageStatus
from app.domains.messaging.repositories import IMessageRepository
from app.infrastructure.persistence.mappers import MessageMapper
from app.database.models import (
    Message as SQLAlchemyMessage,
    Conversation as SQLAlchemyConversation,
    ConversationReadStatus as SQLAlchemyReadStatus,
    MessageStatus as OrmMessageStatus,
)


class SQLAlchemyMessageRepository(IMessageRepository):
    """
    SQLAlchemy implementation of IMessageRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = MessageMapper

    def save(self, message: Message) -> Message:
        """Save message to database."""
        try:
            if message.id is not None:
                return self.update(message)

            db_message = self.mapper.create_orm_instance(message)
            self.db.add(db_message)
            self.db.flush()

            message.id = db_message.id
            return message

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save message: {str(e)}")

    def get_by_id(self, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        try:
            db_message = self.db.query(SQLAlchemyMessage).filter(
                SQLAlchemyMessage.id == message_id,
                SQLAlchemyMessage.deleted_at.is_(None)
            ).first()

            return self.mapper.to_domain(db_message) if db_message else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get message: {str(e)}")

    def get_conversation_messages(
        self,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Message]:
        """
        Get messages for a conversation in chronological order.

        Messages are returned oldest-first (ascending by created_at),
        which is the natural order for chat display where oldest
        messages appear at the top and newest at the bottom.

        For "load more" functionality, increase skip to get older messages.
        """
        try:
            # Count total messages to calculate offset from the end
            total_count = self.db.query(SQLAlchemyMessage).filter(
                SQLAlchemyMessage.conversation_id == conversation_id,
                SQLAlchemyMessage.deleted_at.is_(None)
            ).count()

            # Calculate offset to get the latest 'limit' messages
            # When skip=0, we want the most recent messages
            # When skip>0, we want older messages (for "load more")
            effective_offset = max(0, total_count - limit - skip)
            effective_limit = min(limit, total_count - skip) if skip < total_count else 0

            if effective_limit <= 0:
                return []

            db_messages = self.db.query(SQLAlchemyMessage).filter(
                SQLAlchemyMessage.conversation_id == conversation_id,
                SQLAlchemyMessage.deleted_at.is_(None)
            ).order_by(
                SQLAlchemyMessage.created_at.asc()  # Chronological order: oldest first
            ).offset(effective_offset).limit(effective_limit).all()

            return [self.mapper.to_domain(m) for m in db_messages]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get messages: {str(e)}")

    def update(self, message: Message) -> Message:
        """Update existing message."""
        try:
            db_message = self.db.query(SQLAlchemyMessage).filter(
                SQLAlchemyMessage.id == message.id
            ).first()

            if not db_message:
                raise ValueError(f"Message {message.id} not found")

            self.mapper.update_orm_instance(db_message, message)
            self.db.flush()

            return message

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update message: {str(e)}")

    def update_status_bulk(
        self,
        conversation_id: int,
        up_to_message_id: int,
        exclude_sender_id: int,
        new_status: MessageStatus,
    ) -> int:
        """Update status for multiple messages."""
        try:
            count = self.db.query(SQLAlchemyMessage).filter(
                SQLAlchemyMessage.conversation_id == conversation_id,
                SQLAlchemyMessage.id <= up_to_message_id,
                SQLAlchemyMessage.sender_id != exclude_sender_id,
                SQLAlchemyMessage.status != OrmMessageStatus(new_status.value),
                SQLAlchemyMessage.deleted_at.is_(None)
            ).update(
                {"status": OrmMessageStatus(new_status.value)},
                synchronize_session=False
            )

            self.db.flush()
            return count

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update message statuses: {str(e)}")

    def count_unread_for_user(
        self,
        conversation_id: int,
        user_id: int,
        last_read_message_id: Optional[int],
    ) -> int:
        """Count unread messages for a user in a conversation."""
        try:
            query = self.db.query(SQLAlchemyMessage).filter(
                SQLAlchemyMessage.conversation_id == conversation_id,
                SQLAlchemyMessage.sender_id != user_id,  # Not sent by user
                SQLAlchemyMessage.deleted_at.is_(None)
            )

            if last_read_message_id:
                query = query.filter(SQLAlchemyMessage.id > last_read_message_id)

            return query.count()

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count unread messages: {str(e)}")

    def count_total_unread_for_user(self, user_id: int) -> int:
        """Count total unread messages across all conversations."""
        try:
            # Get all conversations the user is part of
            conversations = self.db.query(SQLAlchemyConversation).filter(
                or_(
                    SQLAlchemyConversation.participant_1_id == user_id,
                    SQLAlchemyConversation.participant_2_id == user_id,
                )
            ).all()

            total = 0
            for conv in conversations:
                # Get read status for this conversation
                read_status = self.db.query(SQLAlchemyReadStatus).filter(
                    SQLAlchemyReadStatus.conversation_id == conv.id,
                    SQLAlchemyReadStatus.user_id == user_id,
                ).first()

                last_read_id = read_status.last_read_message_id if read_status else None

                # Count unread messages
                query = self.db.query(SQLAlchemyMessage).filter(
                    SQLAlchemyMessage.conversation_id == conv.id,
                    SQLAlchemyMessage.sender_id != user_id,
                    SQLAlchemyMessage.deleted_at.is_(None)
                )

                if last_read_id:
                    query = query.filter(SQLAlchemyMessage.id > last_read_id)

                total += query.count()

            return total

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count total unread messages: {str(e)}")
