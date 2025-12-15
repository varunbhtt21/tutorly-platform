"""Message status value object."""

from enum import Enum


class MessageStatus(str, Enum):
    """
    Status of a message in the delivery pipeline.

    SENT: Message has been sent by sender
    DELIVERED: Message has been delivered to recipient's device
    READ: Message has been read by recipient
    """
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"

    @property
    def is_read(self) -> bool:
        """Check if message has been read."""
        return self == MessageStatus.READ

    @property
    def is_delivered(self) -> bool:
        """Check if message has been delivered or read."""
        return self in (MessageStatus.DELIVERED, MessageStatus.READ)

    def __str__(self) -> str:
        return self.value
