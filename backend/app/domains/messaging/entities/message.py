"""Message domain entity."""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from ..value_objects import MessageType, MessageStatus
from ..events import MessageSent, MessageDelivered, MessageRead


@dataclass
class Message:
    """
    Message entity.

    Represents a single message in a conversation.
    """

    # Identity
    id: Optional[int] = None

    # Relationships
    conversation_id: int = field(default=0)
    sender_id: int = field(default=0)
    reply_to_id: Optional[int] = None

    # Content
    content: str = field(default="")
    message_type: MessageType = field(default=MessageType.TEXT)
    status: MessageStatus = field(default=MessageStatus.SENT)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Domain Events (not persisted)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Initialize domain invariants."""
        if not self.conversation_id:
            raise ValueError("Conversation ID is required")
        if not self.sender_id:
            raise ValueError("Sender ID is required")
        if not self.content and self.message_type == MessageType.TEXT:
            raise ValueError("Content is required for text messages")

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        conversation_id: int,
        sender_id: int,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        reply_to_id: Optional[int] = None,
    ) -> "Message":
        """
        Create a new message.

        Args:
            conversation_id: ID of the conversation
            sender_id: ID of the sender
            content: Message content
            message_type: Type of message
            reply_to_id: Optional ID of message being replied to

        Returns:
            New Message instance
        """
        now = datetime.utcnow()

        message = cls(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content.strip(),
            message_type=message_type,
            status=MessageStatus.SENT,
            reply_to_id=reply_to_id,
            created_at=now,
            updated_at=now,
        )

        # Emit domain event
        message._add_domain_event(
            MessageSent(
                message_id=message.id,
                conversation_id=conversation_id,
                sender_id=sender_id,
                message_type=message_type,
                sent_at=now,
            )
        )

        return message

    # ========================================================================
    # Business Logic
    # ========================================================================

    def mark_as_delivered(self) -> None:
        """Mark message as delivered."""
        if self.status == MessageStatus.READ:
            return  # Already read, no need to mark as delivered

        if self.status != MessageStatus.DELIVERED:
            self.status = MessageStatus.DELIVERED
            self.updated_at = datetime.utcnow()

            self._add_domain_event(
                MessageDelivered(
                    message_id=self.id,
                    conversation_id=self.conversation_id,
                    delivered_at=self.updated_at,
                )
            )

    def mark_as_read(self, reader_id: int) -> None:
        """Mark message as read."""
        if self.sender_id == reader_id:
            return  # Sender cannot read their own message

        if self.status != MessageStatus.READ:
            self.status = MessageStatus.READ
            self.updated_at = datetime.utcnow()

            self._add_domain_event(
                MessageRead(
                    message_id=self.id,
                    conversation_id=self.conversation_id,
                    reader_id=reader_id,
                    read_at=self.updated_at,
                )
            )

    @property
    def is_text(self) -> bool:
        """Check if this is a text message."""
        return self.message_type == MessageType.TEXT

    @property
    def is_attachment(self) -> bool:
        """Check if this message has an attachment."""
        return self.message_type.is_attachment

    # ========================================================================
    # Domain Events
    # ========================================================================

    def _add_domain_event(self, event) -> None:
        """Add domain event to event list."""
        self._domain_events.append(event)

    def get_domain_events(self) -> List:
        """Get all domain events."""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Message equality based on ID."""
        if not isinstance(other, Message):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make Message hashable."""
        return hash(self.id) if self.id else hash(id(self))
