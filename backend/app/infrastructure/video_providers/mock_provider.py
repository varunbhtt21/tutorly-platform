"""
Mock Video Provider Implementation.

A mock implementation of IVideoProvider for:
- Local development without API keys
- Unit testing
- Integration testing

This provider simulates all operations without making real API calls.
"""

import uuid
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

from app.domains.classroom.services.video_provider import (
    IVideoProvider,
    RoomConfig,
    RoomInfo,
    RoomToken,
    ParticipantRole,
    RoomNotFoundError,
)

logger = logging.getLogger(__name__)


class MockVideoProvider(IVideoProvider):
    """
    Mock implementation for testing and development.

    Stores rooms in memory and generates fake tokens.
    Useful for:
    - Running tests without Daily.co API
    - Local development without credentials
    - Demo environments
    """

    def __init__(self, domain: str = "mock.daily.co"):
        """Initialize mock provider with in-memory storage."""
        self.domain = domain
        self._rooms: Dict[str, RoomInfo] = {}
        self._active_rooms: set = set()

    @property
    def provider_name(self) -> str:
        return "mock"

    def create_room(self, config: RoomConfig) -> RoomInfo:
        """Create a mock room stored in memory."""
        room_name = f"tutorly-session-{config.session_id}"

        # Check if already exists
        if room_name in self._rooms:
            logger.info(f"Mock room {room_name} already exists, reusing")
            return self._rooms[room_name]

        session_end = config.scheduled_start + timedelta(minutes=config.duration_minutes)
        expiry_time = session_end + timedelta(minutes=30)

        room_info = RoomInfo(
            room_id=str(uuid.uuid4()),
            room_name=room_name,
            room_url=f"https://{self.domain}/{room_name}",
            created_at=datetime.utcnow(),
            expires_at=expiry_time,
            provider=self.provider_name,
        )

        self._rooms[room_name] = room_info
        logger.info(f"Created mock room: {room_name}")

        return room_info

    def get_room(self, room_name: str) -> Optional[RoomInfo]:
        """Get a mock room from memory."""
        return self._rooms.get(room_name)

    def delete_room(self, room_name: str) -> bool:
        """Delete a mock room from memory."""
        if room_name in self._rooms:
            del self._rooms[room_name]
            self._active_rooms.discard(room_name)
            logger.info(f"Deleted mock room: {room_name}")
            return True
        return False

    def create_meeting_token(
        self,
        room_name: str,
        participant_id: int,
        participant_name: str,
        participant_role: ParticipantRole,
        expires_in_minutes: int = 120,
    ) -> RoomToken:
        """Create a mock meeting token."""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

        # Generate a fake JWT-like token
        mock_token = f"mock_token_{room_name}_{participant_id}_{uuid.uuid4().hex[:8]}"
        room_url = f"https://{self.domain}/{room_name}?t={mock_token}"

        logger.info(
            f"Created mock token for {participant_name} "
            f"(role: {participant_role.value}) in room {room_name}"
        )

        return RoomToken(
            token=mock_token,
            room_url=room_url,
            expires_at=expires_at,
            participant_id=participant_id,
            participant_role=participant_role,
            participant_name=participant_name,
        )

    def is_room_active(self, room_name: str) -> bool:
        """Check if a mock room is marked as active."""
        return room_name in self._active_rooms

    # Helper methods for testing
    def set_room_active(self, room_name: str, active: bool = True):
        """Set a room's active status (for testing)."""
        if active:
            self._active_rooms.add(room_name)
        else:
            self._active_rooms.discard(room_name)

    def clear_all_rooms(self):
        """Clear all rooms (for testing)."""
        self._rooms.clear()
        self._active_rooms.clear()
