"""Message repository interface (Port)."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Message
from ..value_objects import MessageStatus


class IMessageRepository(ABC):
    """
    Message repository interface.

    Defines the contract for message persistence.
    Implementation will be in Infrastructure layer (adapter).
    """

    @abstractmethod
    def save(self, message: Message) -> Message:
        """
        Save message to persistence.

        Args:
            message: Message entity

        Returns:
            Saved message with ID
        """
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[Message]:
        """
        Get message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message if found, None otherwise
        """
        pass

    @abstractmethod
    def get_conversation_messages(
        self,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Message]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of messages ordered by created_at desc
        """
        pass

    @abstractmethod
    def update(self, message: Message) -> Message:
        """
        Update existing message.

        Args:
            message: Message entity with changes

        Returns:
            Updated message
        """
        pass

    @abstractmethod
    def update_status_bulk(
        self,
        conversation_id: int,
        up_to_message_id: int,
        exclude_sender_id: int,
        new_status: MessageStatus,
    ) -> int:
        """
        Update status for multiple messages.

        Args:
            conversation_id: Conversation ID
            up_to_message_id: Update messages up to this ID
            exclude_sender_id: Don't update messages from this sender
            new_status: New status to set

        Returns:
            Number of messages updated
        """
        pass

    @abstractmethod
    def count_unread_for_user(
        self,
        conversation_id: int,
        user_id: int,
        last_read_message_id: Optional[int],
    ) -> int:
        """
        Count unread messages for a user in a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (to exclude their own messages)
            last_read_message_id: Last message ID that was read

        Returns:
            Number of unread messages
        """
        pass

    @abstractmethod
    def count_total_unread_for_user(self, user_id: int) -> int:
        """
        Count total unread messages across all conversations.

        Args:
            user_id: User ID

        Returns:
            Total unread count
        """
        pass
