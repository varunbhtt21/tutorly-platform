"""Messaging domain module."""

from .entities import (
    Conversation,
    Message,
    MessageAttachment,
    ConversationReadStatus,
)
from .value_objects import MessageType, MessageStatus
from .repositories import (
    IConversationRepository,
    IMessageRepository,
    IReadStatusRepository,
)

__all__ = [
    # Entities
    "Conversation",
    "Message",
    "MessageAttachment",
    "ConversationReadStatus",
    # Value Objects
    "MessageType",
    "MessageStatus",
    # Repositories
    "IConversationRepository",
    "IMessageRepository",
    "IReadStatusRepository",
]
