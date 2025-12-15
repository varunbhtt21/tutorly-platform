"""Messaging domain repository interfaces."""

from .conversation_repository import IConversationRepository
from .message_repository import IMessageRepository
from .read_status_repository import IReadStatusRepository

__all__ = [
    "IConversationRepository",
    "IMessageRepository",
    "IReadStatusRepository",
]
