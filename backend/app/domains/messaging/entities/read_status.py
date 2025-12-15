"""Conversation read status domain entity."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ConversationReadStatus:
    """
    Tracks the last read message for a user in a conversation.

    Used for calculating unread counts and showing read receipts.
    """

    # Identity
    id: Optional[int] = None

    # Relationships
    conversation_id: int = field(default=0)
    user_id: int = field(default=0)

    # Read tracking
    last_read_message_id: Optional[int] = None
    last_read_at: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize domain invariants."""
        if not self.conversation_id:
            raise ValueError("Conversation ID is required")
        if not self.user_id:
            raise ValueError("User ID is required")

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        conversation_id: int,
        user_id: int,
    ) -> "ConversationReadStatus":
        """
        Create a new read status entry.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user

        Returns:
            New ConversationReadStatus instance
        """
        now = datetime.utcnow()
        return cls(
            conversation_id=conversation_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )

    # ========================================================================
    # Business Logic
    # ========================================================================

    def mark_as_read(self, message_id: int) -> None:
        """Update the last read message."""
        self.last_read_message_id = message_id
        self.last_read_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, ConversationReadStatus):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make ConversationReadStatus hashable."""
        return hash(self.id) if self.id else hash(id(self))
