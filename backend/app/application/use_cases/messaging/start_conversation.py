"""Start conversation use case."""

from app.domains.messaging.entities import Conversation
from app.domains.messaging.repositories import IConversationRepository


class StartConversationUseCase:
    """
    Start or get existing conversation between two users.

    Orchestrates:
    1. Check if conversation already exists
    2. If not, create a new conversation
    """

    def __init__(self, conversation_repo: IConversationRepository):
        """
        Initialize use case.

        Args:
            conversation_repo: Conversation repository
        """
        self.conversation_repo = conversation_repo

    def execute(
        self,
        initiator_id: int,
        recipient_id: int,
    ) -> Conversation:
        """
        Start or get existing conversation.

        Args:
            initiator_id: User who starts the conversation
            recipient_id: User to converse with

        Returns:
            Conversation entity

        Raises:
            ValueError: If trying to start conversation with self
        """
        if initiator_id == recipient_id:
            raise ValueError("Cannot start conversation with yourself")

        # Check for existing conversation
        existing = self.conversation_repo.find_between_users(
            initiator_id, recipient_id
        )

        if existing:
            return existing

        # Create new conversation
        conversation = Conversation.create(
            initiator_id=initiator_id,
            recipient_id=recipient_id,
        )

        # Save and return
        return self.conversation_repo.save(conversation)
