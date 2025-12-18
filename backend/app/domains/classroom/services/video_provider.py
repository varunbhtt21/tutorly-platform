"""
Video Provider Interface (Port).

This is the abstraction layer that decouples the application from specific
video provider implementations. Following the Ports & Adapters pattern,
this interface defines what the application needs from a video provider.

To switch providers (e.g., from Daily.co to Twilio or custom WebRTC):
1. Create a new adapter implementing IVideoProvider
2. Update the dependency injection in dependencies.py
3. No changes needed in use cases, routers, or frontend

Architecture Benefits:
- Provider-agnostic application code
- Easy testing with mock implementations
- Smooth migration path to different providers
- Clear contract for video capabilities
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class ParticipantRole(str, Enum):
    """Role of participant in the video room."""
    INSTRUCTOR = "instructor"
    STUDENT = "student"


@dataclass
class RoomConfig:
    """
    Configuration for creating a video room.

    Attributes:
        session_id: Unique session identifier (links to booking session)
        instructor_id: ID of the instructor
        student_id: ID of the student
        scheduled_start: When the session is scheduled to start
        duration_minutes: Expected duration of the session
        max_participants: Maximum participants allowed (default 2 for 1-on-1)
    """
    session_id: int
    instructor_id: int
    student_id: int
    scheduled_start: datetime
    duration_minutes: int = 60
    max_participants: int = 2


@dataclass
class RoomInfo:
    """
    Information about a created video room.

    Attributes:
        room_id: Provider-specific room identifier
        room_name: Human-readable room name
        room_url: Full URL to join the room (provider-specific)
        created_at: When the room was created
        expires_at: When the room will expire/be deleted
        provider: Name of the video provider (e.g., "daily", "twilio")
    """
    room_id: str
    room_name: str
    room_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    provider: str


@dataclass
class RoomToken:
    """
    Authentication token for joining a video room.

    Attributes:
        token: JWT or provider-specific token for authentication
        room_url: URL to join the room with this token
        expires_at: When this token expires
        participant_id: ID of the participant this token is for
        participant_role: Role of the participant (instructor/student)
        participant_name: Display name in the video call
    """
    token: str
    room_url: str
    expires_at: datetime
    participant_id: int
    participant_role: ParticipantRole
    participant_name: str


class IVideoProvider(ABC):
    """
    Video Provider Interface.

    This interface defines the contract that any video provider implementation
    must fulfill. The application code depends only on this interface, not on
    specific providers like Daily.co or Twilio.

    Implementation Guidelines:
    - All methods should be idempotent where possible
    - Room creation should be atomic
    - Tokens should have appropriate expiration
    - Errors should be raised as VideoProviderError

    Example Implementations:
    - DailyVideoProvider: Uses Daily.co API
    - TwilioVideoProvider: Uses Twilio Video API
    - MockVideoProvider: For testing
    - CustomWebRTCProvider: For self-hosted solution
    """

    @abstractmethod
    def create_room(self, config: RoomConfig) -> RoomInfo:
        """
        Create a new video room for a session.

        Args:
            config: Room configuration including session details

        Returns:
            RoomInfo with room details and join URL

        Raises:
            VideoProviderError: If room creation fails
        """
        pass

    @abstractmethod
    def get_room(self, room_name: str) -> Optional[RoomInfo]:
        """
        Get information about an existing room.

        Args:
            room_name: The room name/identifier

        Returns:
            RoomInfo if room exists, None otherwise
        """
        pass

    @abstractmethod
    def delete_room(self, room_name: str) -> bool:
        """
        Delete a video room.

        Args:
            room_name: The room name/identifier

        Returns:
            True if deleted successfully, False if room didn't exist
        """
        pass

    @abstractmethod
    def create_meeting_token(
        self,
        room_name: str,
        participant_id: int,
        participant_name: str,
        participant_role: ParticipantRole,
        expires_in_minutes: int = 120,
    ) -> RoomToken:
        """
        Create an authentication token for a participant to join a room.

        Args:
            room_name: The room to join
            participant_id: User ID of the participant
            participant_name: Display name in the call
            participant_role: Whether instructor or student
            expires_in_minutes: Token validity period

        Returns:
            RoomToken with authentication details

        Raises:
            VideoProviderError: If token creation fails
        """
        pass

    @abstractmethod
    def is_room_active(self, room_name: str) -> bool:
        """
        Check if a room is currently active (has participants).

        Args:
            room_name: The room name/identifier

        Returns:
            True if room has active participants
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the name of this video provider.

        Returns:
            Provider name (e.g., "daily", "twilio", "custom")
        """
        pass


class VideoProviderError(Exception):
    """
    Base exception for video provider errors.

    Use specific subclasses for different error types.
    """
    pass


class RoomCreationError(VideoProviderError):
    """Raised when room creation fails."""
    pass


class RoomNotFoundError(VideoProviderError):
    """Raised when a room is not found."""
    pass


class TokenCreationError(VideoProviderError):
    """Raised when token creation fails."""
    pass


class ProviderConnectionError(VideoProviderError):
    """Raised when connection to provider fails."""
    pass
