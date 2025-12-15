"""Conversation created domain event."""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ConversationCreated:
    """Domain event emitted when a conversation is created."""

    conversation_id: Optional[int]
    participant_1_id: int
    participant_2_id: int
    created_at: datetime
