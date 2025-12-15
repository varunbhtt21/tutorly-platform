"""Get messages use case."""

from typing import List

from app.domains.messaging.entities import Message
from app.domains.messaging.repositories import (
    IConversationRepository,
    IMessageRepository,
)


class GetMessagesUseCase:
    """
    Get messages for a conversation.

    Orchestrates:
    1. Validate user has access
    2. Fetch messages with pagination
    """

    def __init__(
        self,
        conversation_repo: IConversationRepository,
        message_repo: IMessageRepository,
    ):
        """
        Initialize use case.

        Args:
            conversation_repo: Conversation repository
            message_repo: Message repository
        """
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    def execute(
        self,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Message]:
        """
        Get messages.

        Args:
            conversation_id: Conversation ID
            user_id: User requesting messages
            skip: Number to skip
            limit: Max to return

        Returns:
            List of Message entities

        Raises:
            ValueError: If user doesn't have access
        """
        # Validate access
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        if not conversation.is_participant(user_id):
            raise ValueError("Access denied to this conversation")

        # Get messages
        return self.message_repo.get_conversation_messages(
            conversation_id=conversation_id,
            skip=skip,
            limit=limit,
        )
