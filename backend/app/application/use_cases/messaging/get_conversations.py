"""Get conversations use case."""

from typing import List, Dict, Any

from app.domains.messaging.repositories import (
    IConversationRepository,
    IMessageRepository,
    IReadStatusRepository,
)


class GetConversationsUseCase:
    """
    Get all conversations for a user with unread counts.

    Orchestrates:
    1. Fetch user's conversations
    2. Calculate unread counts for each
    3. Return enriched data
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
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get conversations with metadata.

        Args:
            user_id: User ID
            skip: Number to skip
            limit: Max to return

        Returns:
            List of conversation dicts with unread_count
        """
        # Get conversations
        conversations = self.conversation_repo.get_user_conversations(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        # Get read statuses
        read_statuses = self.read_status_repo.get_user_read_statuses(user_id)

        # Enrich with unread counts
        result = []
        for conv in conversations:
            read_status = read_statuses.get(conv.id)
            last_read_id = read_status.last_read_message_id if read_status else None

            unread_count = self.message_repo.count_unread_for_user(
                conversation_id=conv.id,
                user_id=user_id,
                last_read_message_id=last_read_id,
            )

            result.append({
                "conversation": conv,
                "unread_count": unread_count,
            })

        return result
