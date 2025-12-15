"""Message read domain event."""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MessageRead:
    """Domain event emitted when a message is read."""

    message_id: Optional[int]
    conversation_id: int
    reader_id: int
    read_at: datetime
