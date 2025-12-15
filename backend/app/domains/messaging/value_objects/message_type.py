"""Message type value object."""

from enum import Enum


class MessageType(str, Enum):
    """
    Types of messages that can be sent.

    TEXT: Plain text message (available before booking)
    IMAGE: Image attachment (requires booking)
    FILE: File attachment (requires booking)
    SYSTEM: System-generated messages
    """
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"

    @property
    def requires_booking(self) -> bool:
        """Check if this message type requires a booking to be created."""
        return self in (MessageType.IMAGE, MessageType.FILE)

    @property
    def is_attachment(self) -> bool:
        """Check if this message type is an attachment."""
        return self in (MessageType.IMAGE, MessageType.FILE)

    def __str__(self) -> str:
        return self.value
