"""Message sent domain event."""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from ..value_objects import MessageType


@dataclass(frozen=True)
class MessageSent:
    """Domain event emitted when a message is sent."""

    message_id: Optional[int]
    conversation_id: int
    sender_id: int
    message_type: MessageType
    sent_at: datetime
