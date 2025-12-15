"""Message delivered domain event."""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MessageDelivered:
    """Domain event emitted when a message is delivered."""

    message_id: Optional[int]
    conversation_id: int
    delivered_at: datetime
