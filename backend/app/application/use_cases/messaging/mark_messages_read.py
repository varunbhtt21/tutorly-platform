"""Mark messages as read use case."""

from app.domains.messaging.entities import ConversationReadStatus
from app.domains.messaging.value_objects import MessageStatus
from app.domains.messaging.repositories import (
    IConversationRepository,
    IMessageRepository,
    IReadStatusRepository,
)


class MarkMessagesReadUseCase:
    """
    Mark messages as read up to a certain message.

    Orchestrates:
    1. Validate user access
    2. Update message statuses
    3. Update read status tracking
    """

    def __init__(
        self,
        conversation_repo: IConversationRepository,
        message_repo: IMessageRepository,
        read_status_repo: IReadStatusRepository,
    ):
        """
        Initialize use case.

        Args:
            conversation_repo: Conversation repository
            message_repo: Message repository
            read_status_repo: Read status repository
        """
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.read_status_repo = read_status_repo

    def execute(
        self,
        conversation_id: int,
        user_id: int,
        message_id: int,
    ) -> int:
        """
        Mark messages as read.

        Args:
            conversation_id: Conversation ID
            user_id: User marking as read
            message_id: Mark all messages up to this ID as read

        Returns:
            Number of messages marked as read

        Raises:
            ValueError: If user doesn't have access
        """
        # Validate access
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        if not conversation.is_participant(user_id):
            raise ValueError("Access denied to this conversation")

        # Update message statuses
        updated_count = self.message_repo.update_status_bulk(
            conversation_id=conversation_id,
            up_to_message_id=message_id,
            exclude_sender_id=user_id,  # Don't mark own messages as read
            new_status=MessageStatus.READ,
        )

        # Update or create read status
        read_status = self.read_status_repo.get_by_conversation_and_user(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if read_status:
            read_status.mark_as_read(message_id)
            self.read_status_repo.update(read_status)
        else:
            new_status = ConversationReadStatus.create(
                conversation_id=conversation_id,
                user_id=user_id,
            )
            new_status.mark_as_read(message_id)
            self.read_status_repo.save(new_status)

        return updated_count
