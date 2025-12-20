"""
100ms Video Provider Implementation.

This adapter implements the IVideoProvider interface using 100ms REST API.
100ms provides WebRTC-based video calling with role-based access control.

API Documentation: https://www.100ms.live/docs/server-side/v2/api-reference

Configuration:
- HMS_ACCESS_KEY: Your 100ms access key (from dashboard)
- HMS_APP_SECRET: Your 100ms app secret (for token generation)
- HMS_TEMPLATE_ID: Default template ID for rooms (optional)

Usage:
    provider = HundredMsVideoProvider(
        access_key="your-access-key",
        app_secret="your-app-secret",
    )
    room = provider.create_room(config)
    token = provider.create_meeting_token(room.room_name, ...)

Note on Architecture:
    This provider follows the same interface as DailyVideoProvider,
    making it easy to switch between providers via configuration.
    The application code remains unchanged regardless of which
    provider is active.

Future Migration Path:
    To add Jitsi support, create a JitsiVideoProvider following
    the same pattern. The provider interface supports:
    - Self-hosted solutions (Jitsi)
    - Cloud providers (Daily.co, 100ms, Twilio)
    - Hybrid approaches
"""

import jwt
import uuid
import logging
import requests
from typing import Optional
from datetime import datetime, timedelta, timezone

from app.domains.classroom.services.video_provider import (
    IVideoProvider,
    RoomConfig,
    RoomInfo,
    RoomToken,
    ParticipantRole,
    RoomCreationError,
    RoomNotFoundError,
    TokenCreationError,
    ProviderConnectionError,
)

logger = logging.getLogger(__name__)


class HundredMsVideoProvider(IVideoProvider):
    """
    100ms implementation of the Video Provider interface.

    100ms is a WebRTC platform that provides:
    - Video/audio rooms with role-based permissions
    - JWT-based authentication (self-signed)
    - Templates for room configuration
    - Recording and live streaming capabilities

    Key Differences from Daily.co:
    - Uses management tokens for API auth (self-signed JWT)
    - Rooms are identified by room_id, not name
    - Tokens are generated client-side using app secret
    - Role-based permissions via templates

    Attributes:
        access_key: 100ms access key for authentication
        app_secret: 100ms app secret for token generation
        template_id: Optional default template for rooms
        base_url: 100ms API base URL
    """

    BASE_URL = "https://api.100ms.live/v2"

    def __init__(
        self,
        access_key: str,
        app_secret: str,
        template_id: Optional[str] = None,
    ):
        """
        Initialize 100ms provider.

        Args:
            access_key: 100ms access key (from dashboard)
            app_secret: 100ms app secret (for JWT signing)
            template_id: Optional default template ID for rooms
        """
        self.access_key = access_key
        self.app_secret = app_secret
        self.template_id = template_id
        self._room_cache: dict[str, str] = {}  # room_name -> room_id mapping

    @property
    def provider_name(self) -> str:
        return "hundredms"

    def _generate_management_token(self, expires_in_seconds: int = 86400) -> str:
        """
        Generate a management token for 100ms API authentication.

        100ms uses self-signed JWT tokens for API authentication.
        This is different from Daily.co which uses a simple API key.

        Args:
            expires_in_seconds: Token validity (default 24 hours)

        Returns:
            JWT management token string
        """
        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=expires_in_seconds)

        payload = {
            "access_key": self.access_key,
            "type": "management",
            "version": 2,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(payload, self.app_secret, algorithm="HS256")

    def _get_headers(self) -> dict:
        """Get headers with fresh management token."""
        return {
            "Authorization": f"Bearer {self._generate_management_token()}",
            "Content-Type": "application/json",
        }

    def create_room(self, config: RoomConfig) -> RoomInfo:
        """
        Create a 100ms room for a tutoring session.

        Room naming convention: tutorly-session-{session_id}
        This ensures unique rooms per session and easy identification.

        100ms Room Configuration:
        - Uses template for role permissions (if configured)
        - Room is enabled by default
        - Recording can be enabled via template

        Args:
            config: Room configuration with session details

        Returns:
            RoomInfo with room details and join URL

        Raises:
            RoomCreationError: If room creation fails
        """
        room_name = f"tutorly-session-{config.session_id}"

        # Check if room already exists (idempotency)
        existing = self.get_room(room_name)
        if existing:
            logger.info(f"Room {room_name} already exists, reusing")
            return existing

        # Room configuration for 100ms
        room_config = {
            "name": room_name,
            "description": f"Tutoring session {config.session_id}",
            "recording_info": {
                "enabled": False,  # Can enable if recording is needed
            },
        }

        # Add template if configured
        if self.template_id:
            room_config["template_id"] = self.template_id

        try:
            response = requests.post(
                f"{self.BASE_URL}/rooms",
                json=room_config,
                headers=self._get_headers(),
                timeout=30,
            )

            if response.status_code == 400:
                error_data = response.json()
                logger.error(f"100ms room creation failed: {error_data}")

                # Check if room already exists (race condition handling)
                if "already exists" in str(error_data).lower():
                    existing = self.get_room(room_name)
                    if existing:
                        return existing

                raise RoomCreationError(f"100ms API error: {error_data}")

            if response.status_code == 401:
                logger.error("100ms authentication failed - check access_key and app_secret")
                raise ProviderConnectionError("100ms authentication failed")

            response.raise_for_status()
            data = response.json()

            room_id = data["id"]

            # Cache room_id for later lookups
            self._room_cache[room_name] = room_id

            # Calculate expiry (session end + 30 min buffer)
            scheduled_start = config.scheduled_start
            if scheduled_start.tzinfo is None:
                scheduled_start = scheduled_start.replace(tzinfo=timezone.utc)

            session_end = scheduled_start + timedelta(minutes=config.duration_minutes)
            expires_at = session_end + timedelta(minutes=30)

            logger.info(f"Created 100ms room: {room_name} (ID: {room_id})")

            return RoomInfo(
                room_id=room_id,
                room_name=room_name,
                room_url=self._build_room_url(room_id, room_name),
                created_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                provider=self.provider_name,
            )

        except requests.exceptions.Timeout:
            logger.error(f"Timeout creating room {room_name}")
            raise ProviderConnectionError("100ms API timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create room {room_name}: {e}")
            raise RoomCreationError(f"Failed to create 100ms room: {str(e)}")

    def _build_room_url(self, room_id: str, room_name: str) -> str:
        """
        Build the room URL for 100ms.

        100ms doesn't have a direct join URL like Daily.co.
        The frontend uses the room_id with 100ms SDK to join.
        This URL is informational and used by frontend to construct join logic.

        Args:
            room_id: 100ms room ID
            room_name: Human-readable room name

        Returns:
            Room identifier URL (used by frontend for joining)
        """
        # 100ms uses room codes or room IDs for joining
        # The actual join happens via SDK, so we return room_id reference
        return f"100ms://{room_id}/{room_name}"

    def get_room(self, room_name: str) -> Optional[RoomInfo]:
        """
        Get information about an existing 100ms room.

        100ms allows filtering rooms by name, which we use for lookup.

        Args:
            room_name: The room name to look up

        Returns:
            RoomInfo if room exists, None otherwise
        """
        try:
            # 100ms API supports filtering by name
            response = requests.get(
                f"{self.BASE_URL}/rooms",
                params={"name": room_name},
                headers=self._get_headers(),
                timeout=30,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            # Response contains a list of rooms matching the filter
            rooms = data.get("data", [])
            if not rooms:
                return None

            room = rooms[0]  # Get first matching room
            room_id = room["id"]

            # Cache for future lookups
            self._room_cache[room_name] = room_id

            # Parse created_at timestamp
            created_at = datetime.now(timezone.utc)
            if "created_at" in room:
                try:
                    created_at = datetime.fromisoformat(
                        room["created_at"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass

            return RoomInfo(
                room_id=room_id,
                room_name=room["name"],
                room_url=self._build_room_url(room_id, room["name"]),
                created_at=created_at,
                expires_at=None,  # 100ms rooms don't auto-expire
                provider=self.provider_name,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get room {room_name}: {e}")
            return None

    def _get_room_id(self, room_name: str) -> Optional[str]:
        """
        Get room_id from room_name, using cache or API lookup.

        Args:
            room_name: The room name

        Returns:
            Room ID if found, None otherwise
        """
        # Check cache first
        if room_name in self._room_cache:
            return self._room_cache[room_name]

        # Fetch from API
        room = self.get_room(room_name)
        if room:
            return room.room_id
        return None

    def delete_room(self, room_name: str) -> bool:
        """
        Delete/disable a 100ms room.

        100ms doesn't actually delete rooms, but we can disable them.

        Args:
            room_name: The room name to delete

        Returns:
            True if disabled successfully, False if room didn't exist
        """
        try:
            room_id = self._get_room_id(room_name)
            if not room_id:
                logger.info(f"Room {room_name} not found for deletion")
                return False

            # 100ms uses POST to disable rooms
            response = requests.post(
                f"{self.BASE_URL}/rooms/{room_id}",
                json={"enabled": False},
                headers=self._get_headers(),
                timeout=30,
            )

            if response.status_code == 404:
                logger.info(f"Room {room_name} not found for deletion")
                return False

            response.raise_for_status()

            # Remove from cache
            self._room_cache.pop(room_name, None)

            logger.info(f"Disabled 100ms room: {room_name}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete room {room_name}: {e}")
            return False

    def create_meeting_token(
        self,
        room_name: str,
        participant_id: int,
        participant_name: str,
        participant_role: ParticipantRole,
        expires_in_minutes: int = 120,
    ) -> RoomToken:
        """
        Create a meeting token for a participant.

        100ms uses self-signed JWT tokens (auth tokens) for participants.
        This is generated locally without API call, using the app_secret.

        Token includes:
        - Room ID for access control
        - User ID and name for identification
        - Role for permissions (host/guest)
        - Expiration time

        Args:
            room_name: The room to join
            participant_id: User ID of the participant
            participant_name: Display name in the call
            participant_role: Whether instructor or student
            expires_in_minutes: Token validity period

        Returns:
            RoomToken with authentication details

        Raises:
            TokenCreationError: If token creation fails
        """
        try:
            # Get room_id from room_name
            room_id = self._get_room_id(room_name)
            if not room_id:
                raise TokenCreationError(f"Room {room_name} not found")

            # Map role to 100ms role names
            # Default template has "host" and "guest" roles
            hms_role = "host" if participant_role == ParticipantRole.INSTRUCTOR else "guest"

            # Calculate expiration
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=expires_in_minutes)

            # Build JWT payload for 100ms auth token
            payload = {
                "access_key": self.access_key,
                "type": "app",
                "version": 2,
                "room_id": room_id,
                "user_id": str(participant_id),
                "role": hms_role,
                "iat": int(now.timestamp()),
                "exp": int(expires_at.timestamp()),
                "jti": str(uuid.uuid4()),
            }

            # Sign the token
            token = jwt.encode(payload, self.app_secret, algorithm="HS256")

            # Build room URL with token
            # Frontend will use this to initialize 100ms SDK
            room_url = f"100ms://{room_id}/{room_name}?token={token}"

            logger.info(
                f"Created 100ms meeting token for {participant_name} "
                f"(role: {participant_role.value}) in room {room_name}"
            )

            return RoomToken(
                token=token,
                room_url=room_url,
                expires_at=expires_at,
                participant_id=participant_id,
                participant_role=participant_role,
                participant_name=participant_name,
            )

        except Exception as e:
            logger.error(f"Failed to create token for room {room_name}: {e}")
            raise TokenCreationError(f"Failed to create meeting token: {str(e)}")

    def is_room_active(self, room_name: str) -> bool:
        """
        Check if a room has active participants.

        100ms provides active room sessions via API.

        Args:
            room_name: The room name to check

        Returns:
            True if room has active participants
        """
        try:
            room_id = self._get_room_id(room_name)
            if not room_id:
                return False

            # Get active sessions for the room
            response = requests.get(
                f"{self.BASE_URL}/active-rooms/{room_id}",
                headers=self._get_headers(),
                timeout=30,
            )

            if response.status_code == 404:
                return False

            response.raise_for_status()
            data = response.json()

            # Check if there are any peers in the room
            peer_count = data.get("peer_count", 0)
            return peer_count > 0

        except requests.exceptions.RequestException:
            return False

    def get_room_code(self, room_name: str, role: str = "guest") -> Optional[str]:
        """
        Get a room code for easy joining (100ms specific feature).

        Room codes are short codes that can be shared for joining rooms.
        This is an optional convenience method specific to 100ms.

        Args:
            room_name: The room name
            role: Role for the room code (host/guest)

        Returns:
            Room code string if available, None otherwise
        """
        try:
            room_id = self._get_room_id(room_name)
            if not room_id:
                return None

            response = requests.post(
                f"{self.BASE_URL}/room-codes/room/{room_id}",
                headers=self._get_headers(),
                timeout=30,
            )

            if response.status_code != 200:
                return None

            data = response.json()

            # Find code for the requested role
            codes = data.get("data", [])
            for code in codes:
                if code.get("role") == role:
                    return code.get("code")

            return None

        except requests.exceptions.RequestException:
            return None
