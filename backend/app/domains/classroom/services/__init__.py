"""
Classroom Domain Services.

Contains:
1. Video Provider interface - abstraction layer for video providers
2. ClassroomService - domain service for classroom lifecycle management
"""

from .video_provider import (
    IVideoProvider,
    RoomConfig,
    RoomInfo,
    RoomToken,
    ParticipantRole,
    RoomNotFoundError,
    RoomCreationError,
    TokenCreationError,
)
from .classroom_service import ClassroomService

__all__ = [
    "IVideoProvider",
    "RoomConfig",
    "RoomInfo",
    "RoomToken",
    "ParticipantRole",
    "RoomNotFoundError",
    "RoomCreationError",
    "TokenCreationError",
    "ClassroomService",
]
