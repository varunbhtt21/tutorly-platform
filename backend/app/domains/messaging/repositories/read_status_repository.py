"""Read status repository interface (Port)."""

from abc import ABC, abstractmethod
from typing import Optional, Dict

from ..entities import ConversationReadStatus


class IReadStatusRepository(ABC):
    """
    Read status repository interface.

    Defines the contract for read status persistence.
    Implementation will be in Infrastructure layer (adapter).
    """

    @abstractmethod
    def save(self, read_status: ConversationReadStatus) -> ConversationReadStatus:
        """
        Save read status to persistence.

        Args:
            read_status: ConversationReadStatus entity

        Returns:
            Saved read status with ID
        """
        pass

    @abstractmethod
    def get_by_conversation_and_user(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Optional[ConversationReadStatus]:
        """
        Get read status for a user in a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            ConversationReadStatus if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_read_statuses(
        self,
        user_id: int,
    ) -> Dict[int, ConversationReadStatus]:
        """
        Get all read statuses for a user.

        Args:
            user_id: User ID

        Returns:
            Dict mapping conversation_id to ConversationReadStatus
        """
        pass

    @abstractmethod
    def update(self, read_status: ConversationReadStatus) -> ConversationReadStatus:
        """
        Update existing read status.

        Args:
            read_status: ConversationReadStatus entity with changes

        Returns:
            Updated read status
        """
        pass
