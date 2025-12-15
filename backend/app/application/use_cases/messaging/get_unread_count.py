"""Get total unread count use case."""

from app.domains.messaging.repositories import IMessageRepository


class GetUnreadCountUseCase:
    """
    Get total unread message count for a user.

    Used for notification badges.
    """

    def __init__(self, message_repo: IMessageRepository):
        """
        Initialize use case.

        Args:
            message_repo: Message repository
        """
        self.message_repo = message_repo

    def execute(self, user_id: int) -> int:
        """
        Get total unread count.

        Args:
            user_id: User ID

        Returns:
            Total unread message count
        """
        return self.message_repo.count_total_unread_for_user(user_id)
