"""Check feature access use case."""

from dataclasses import dataclass
from typing import Protocol

from app.domains.messaging.value_objects import MessageType


class ISessionRepository(Protocol):
    """Protocol for checking session existence."""

    def has_booked_session_between(
        self,
        user_1_id: int,
        user_2_id: int,
    ) -> bool:
        """Check if any session exists between two users."""
        ...


@dataclass
class FeatureAccess:
    """Feature access result."""

    can_send_text: bool
    can_send_image: bool
    can_send_file: bool
    has_booking: bool

    def can_send_message_type(self, message_type: MessageType) -> bool:
        """Check if can send a specific message type."""
        if message_type == MessageType.TEXT:
            return self.can_send_text
        elif message_type == MessageType.IMAGE:
            return self.can_send_image
        elif message_type == MessageType.FILE:
            return self.can_send_file
        elif message_type == MessageType.SYSTEM:
            return True
        return False


class CheckFeatureAccessUseCase:
    """
    Check what messaging features a user has access to.

    Feature gating logic:
    - Before booking: Only text messages allowed
    - After booking: All features (images, files) unlocked
    """

    def __init__(self, session_repo: ISessionRepository):
        """
        Initialize use case.

        Args:
            session_repo: Session repository for checking bookings
        """
        self.session_repo = session_repo

    def execute(
        self,
        user_id: int,
        other_user_id: int,
    ) -> FeatureAccess:
        """
        Check feature access between two users.

        Args:
            user_id: Current user ID
            other_user_id: Other user ID

        Returns:
            FeatureAccess with available features
        """
        # Check if any booking exists between users
        has_booking = self.session_repo.has_booked_session_between(
            user_1_id=user_id,
            user_2_id=other_user_id,
        )

        return FeatureAccess(
            can_send_text=True,  # Always allowed
            can_send_image=has_booking,
            can_send_file=has_booking,
            has_booking=has_booking,
        )
