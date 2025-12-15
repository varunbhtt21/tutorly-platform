"""SQLAlchemy implementation of Conversation repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, desc, case

from app.domains.messaging.entities import Conversation
from app.domains.messaging.repositories import IConversationRepository
from app.infrastructure.persistence.mappers import ConversationMapper
from app.database.models import Conversation as SQLAlchemyConversation


class SQLAlchemyConversationRepository(IConversationRepository):
    """
    SQLAlchemy implementation of IConversationRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = ConversationMapper

    def save(self, conversation: Conversation) -> Conversation:
        """Save conversation to database."""
        try:
            if conversation.id is not None:
                return self.update(conversation)

            db_conversation = self.mapper.create_orm_instance(conversation)
            self.db.add(db_conversation)
            self.db.flush()

            conversation.id = db_conversation.id
            return conversation

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save conversation: {str(e)}")

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        try:
            db_conversation = self.db.query(SQLAlchemyConversation).filter(
                SQLAlchemyConversation.id == conversation_id
            ).first()

            return self.mapper.to_domain(db_conversation) if db_conversation else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get conversation: {str(e)}")

    def find_between_users(
        self,
        user_1_id: int,
        user_2_id: int
    ) -> Optional[Conversation]:
        """Find existing conversation between two users."""
        try:
            db_conversation = self.db.query(SQLAlchemyConversation).filter(
                or_(
                    (SQLAlchemyConversation.participant_1_id == user_1_id) &
                    (SQLAlchemyConversation.participant_2_id == user_2_id),
                    (SQLAlchemyConversation.participant_1_id == user_2_id) &
                    (SQLAlchemyConversation.participant_2_id == user_1_id),
                )
            ).first()

            return self.mapper.to_domain(db_conversation) if db_conversation else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to find conversation: {str(e)}")

    def get_user_conversations(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Conversation]:
        """Get all conversations for a user."""
        try:
            # Use CASE expression for SQLite compatibility (doesn't support NULLS LAST)
            # This puts NULLs last by sorting: non-null values first (0), then nulls (1)
            null_last_order = case(
                (SQLAlchemyConversation.last_message_at.is_(None), 1),
                else_=0
            )
            db_conversations = self.db.query(SQLAlchemyConversation).filter(
                or_(
                    SQLAlchemyConversation.participant_1_id == user_id,
                    SQLAlchemyConversation.participant_2_id == user_id,
                )
            ).order_by(
                null_last_order,
                desc(SQLAlchemyConversation.last_message_at),
                desc(SQLAlchemyConversation.created_at)
            ).offset(skip).limit(limit).all()

            return [self.mapper.to_domain(c) for c in db_conversations]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get conversations: {str(e)}")

    def update(self, conversation: Conversation) -> Conversation:
        """Update existing conversation."""
        try:
            db_conversation = self.db.query(SQLAlchemyConversation).filter(
                SQLAlchemyConversation.id == conversation.id
            ).first()

            if not db_conversation:
                raise ValueError(f"Conversation {conversation.id} not found")

            self.mapper.update_orm_instance(db_conversation, conversation)
            self.db.flush()

            return conversation

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update conversation: {str(e)}")

    def count_user_conversations(self, user_id: int) -> int:
        """Count conversations for a user."""
        try:
            return self.db.query(SQLAlchemyConversation).filter(
                or_(
                    SQLAlchemyConversation.participant_1_id == user_id,
                    SQLAlchemyConversation.participant_2_id == user_id,
                )
            ).count()

        except SQLAlchemyError as e:
            raise Exception(f"Failed to count conversations: {str(e)}")
