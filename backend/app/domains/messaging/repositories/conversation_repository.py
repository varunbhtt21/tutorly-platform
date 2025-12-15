"""Conversation repository interface (Port)."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from ..entities import Conversation


class IConversationRepository(ABC):
    """
    Conversation repository interface.

    Defines the contract for conversation persistence.
    Implementation will be in Infrastructure layer (adapter).
    """

    @abstractmethod
    def save(self, conversation: Conversation) -> Conversation:
        """
        Save conversation to persistence.

        Args:
            conversation: Conversation entity

        Returns:
            Saved conversation with ID
        """
        pass

    @abstractmethod
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """
        Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    def find_between_users(
        self,
        user_1_id: int,
        user_2_id: int
    ) -> Optional[Conversation]:
        """
        Find existing conversation between two users.

        Args:
            user_1_id: First user ID
            user_2_id: Second user ID

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_conversations(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Conversation]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of conversations ordered by last_message_at desc
        """
        pass

    @abstractmethod
    def update(self, conversation: Conversation) -> Conversation:
        """
        Update existing conversation.

        Args:
            conversation: Conversation entity with changes

        Returns:
            Updated conversation
        """
        pass

    @abstractmethod
    def count_user_conversations(self, user_id: int) -> int:
        """
        Count conversations for a user.

        Args:
            user_id: User ID

        Returns:
            Number of conversations
        """
        pass
