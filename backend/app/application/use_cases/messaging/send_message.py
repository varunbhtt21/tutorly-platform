"""Send message use case."""

from typing import Optional

from app.domains.messaging.entities import Message, Conversation
from app.domains.messaging.value_objects import MessageType
from app.domains.messaging.repositories import (
    IConversationRepository,
    IMessageRepository,
)


class SendMessageUseCase:
    """
    Send a message in a conversation.

    Orchestrates:
    1. Validate user has access to conversation
    2. Create message entity
    3. Update conversation's last message
    4. Persist changes
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
        sender_id: int,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        reply_to_id: Optional[int] = None,
    ) -> Message:
        """
        Send a message.

        Args:
            conversation_id: ID of the conversation
            sender_id: ID of the sender
            content: Message content
            message_type: Type of message
            reply_to_id: Optional ID of message being replied to

        Returns:
            Created Message entity

        Raises:
            ValueError: If user doesn't have access or content is empty
        """
        # Get conversation
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Validate access
        if not conversation.is_participant(sender_id):
            raise ValueError("Access denied to this conversation")

        # Validate content
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        # Create message
        message = Message.create(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            reply_to_id=reply_to_id,
        )

        # Save message
        saved_message = self.message_repo.save(message)

        # Update conversation's last message
        conversation.update_last_message(
            message_id=saved_message.id,
            sent_at=saved_message.created_at,
        )
        self.conversation_repo.update(conversation)

        return saved_message
