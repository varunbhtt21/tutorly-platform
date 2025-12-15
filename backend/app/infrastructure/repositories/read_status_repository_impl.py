"""SQLAlchemy implementation of ReadStatus repository."""

from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.domains.messaging.entities import ConversationReadStatus
from app.domains.messaging.repositories import IReadStatusRepository
from app.infrastructure.persistence.mappers import ReadStatusMapper
from app.database.models import ConversationReadStatus as SQLAlchemyReadStatus


class SQLAlchemyReadStatusRepository(IReadStatusRepository):
    """
    SQLAlchemy implementation of IReadStatusRepository.

    Adapts domain repository interface to SQLAlchemy ORM.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = ReadStatusMapper

    def save(self, read_status: ConversationReadStatus) -> ConversationReadStatus:
        """Save read status to database."""
        try:
            if read_status.id is not None:
                return self.update(read_status)

            db_status = self.mapper.create_orm_instance(read_status)
            self.db.add(db_status)
            self.db.flush()

            read_status.id = db_status.id
            return read_status

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save read status: {str(e)}")

    def get_by_conversation_and_user(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Optional[ConversationReadStatus]:
        """Get read status for a user in a conversation."""
        try:
            db_status = self.db.query(SQLAlchemyReadStatus).filter(
                SQLAlchemyReadStatus.conversation_id == conversation_id,
                SQLAlchemyReadStatus.user_id == user_id,
            ).first()

            return self.mapper.to_domain(db_status) if db_status else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get read status: {str(e)}")

    def get_user_read_statuses(
        self,
        user_id: int,
    ) -> Dict[int, ConversationReadStatus]:
        """Get all read statuses for a user."""
        try:
            db_statuses = self.db.query(SQLAlchemyReadStatus).filter(
                SQLAlchemyReadStatus.user_id == user_id,
            ).all()

            return {
                s.conversation_id: self.mapper.to_domain(s)
                for s in db_statuses
            }

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get read statuses: {str(e)}")

    def update(self, read_status: ConversationReadStatus) -> ConversationReadStatus:
        """Update existing read status."""
        try:
            db_status = self.db.query(SQLAlchemyReadStatus).filter(
                SQLAlchemyReadStatus.id == read_status.id
            ).first()

            if not db_status:
                raise ValueError(f"Read status {read_status.id} not found")

            self.mapper.update_orm_instance(db_status, read_status)
            self.db.flush()

            return read_status

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update read status: {str(e)}")
