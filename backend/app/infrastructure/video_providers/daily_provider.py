"""
Daily.co Video Provider Implementation.

This adapter implements the IVideoProvider interface using Daily.co's REST API.
Daily.co provides WebRTC-based video calling with a simple API.

API Documentation: https://docs.daily.co/reference/rest-api

Configuration:
- DAILY_API_KEY: Your Daily.co API key (from dashboard)
- DAILY_DOMAIN: Your Daily.co domain (e.g., "your-domain.daily.co")

Usage:
    provider = DailyVideoProvider(
        api_key="your-api-key",
        domain="your-domain.daily.co"
    )
    room = provider.create_room(config)
    token = provider.create_meeting_token(room.room_name, ...)
"""

import requests
import jwt
import time
import logging
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


class DailyVideoProvider(IVideoProvider):
    """
    Daily.co implementation of the Video Provider interface.

    Daily.co is a WebRTC platform that provides:
    - Video/audio rooms with simple API
    - JWT-based authentication for participants
    - No additional client-side infrastructure needed

    Attributes:
        api_key: Daily.co API key for authentication
        domain: Your Daily.co subdomain (e.g., "tutorly.daily.co")
        base_url: Daily.co API base URL
    """

    BASE_URL = "https://api.daily.co/v1"

    def __init__(self, api_key: str, domain: str):
        """
        Initialize Daily.co provider.

        Args:
            api_key: Daily.co API key (starts with "d...")
            domain: Your Daily.co domain (e.g., "tutorly.daily.co")
        """
        self.api_key = api_key
        self.domain = domain
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    @property
    def provider_name(self) -> str:
        return "daily"

    def create_room(self, config: RoomConfig) -> RoomInfo:
        """
        Create a Daily.co room for a tutoring session.

        Room naming convention: tutorly-session-{session_id}
        This ensures unique rooms per session and easy identification.

        The room is configured with:
        - Privacy enabled (require token to join)
        - Auto-expiry after session end time + buffer
        - Max 2 participants for 1-on-1 tutoring
        """
        room_name = f"tutorly-session-{config.session_id}"

        # Calculate room expiry (session end + 30 min buffer)
        # Ensure we treat naive datetimes as UTC for correct timestamp calculation
        scheduled_start = config.scheduled_start
        if scheduled_start.tzinfo is None:
            # Naive datetime - assume UTC
            scheduled_start = scheduled_start.replace(tzinfo=timezone.utc)

        session_end = scheduled_start + timedelta(minutes=config.duration_minutes)
        expiry_time = session_end + timedelta(minutes=30)
        exp_timestamp = int(expiry_time.timestamp())

        # Room configuration for Daily.co
        room_config = {
            "name": room_name,
            "privacy": "private",  # Requires meeting token to join
            "properties": {
                "max_participants": config.max_participants,
                "exp": exp_timestamp,  # Room expires after this time
                "enable_chat": True,
                "enable_screenshare": True,
                "enable_knocking": False,  # Direct join with token
                "start_video_off": False,
                "start_audio_off": False,
                "enable_prejoin_ui": True,  # Show preview before joining
                "eject_at_room_exp": True,  # Kick everyone when room expires
            },
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/rooms",
                json=room_config,
                headers=self._headers,
                timeout=30,
            )

            if response.status_code == 400:
                # Log the actual error from Daily.co
                logger.error(f"Daily.co room creation failed: {response.text}")
                # Room might already exist, try to get it
                existing = self.get_room(room_name)
                if existing:
                    logger.info(f"Room {room_name} already exists, reusing")
                    return existing
                # If room doesn't exist and we got 400, raise with details
                raise RoomCreationError(f"Daily.co API error: {response.text}")

            response.raise_for_status()
            data = response.json()

            logger.info(f"Created Daily.co room: {room_name}")

            return RoomInfo(
                room_id=data.get("id", room_name),
                room_name=data["name"],
                room_url=data["url"],
                created_at=datetime.now(timezone.utc),
                expires_at=expiry_time,
                provider=self.provider_name,
            )

        except requests.exceptions.Timeout:
            logger.error(f"Timeout creating room {room_name}")
            raise ProviderConnectionError("Daily.co API timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create room {room_name}: {e}")
            raise RoomCreationError(f"Failed to create Daily.co room: {str(e)}")

    def get_room(self, room_name: str) -> Optional[RoomInfo]:
        """Get information about an existing Daily.co room."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/rooms/{room_name}",
                headers=self._headers,
                timeout=30,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            # Parse expiry time (UTC timestamp from Daily.co)
            exp_timestamp = data.get("config", {}).get("exp")
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) if exp_timestamp else None

            return RoomInfo(
                room_id=data.get("id", room_name),
                room_name=data["name"],
                room_url=data["url"],
                created_at=datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                ) if "created_at" in data else datetime.now(timezone.utc),
                expires_at=expires_at,
                provider=self.provider_name,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get room {room_name}: {e}")
            return None

    def delete_room(self, room_name: str) -> bool:
        """Delete a Daily.co room."""
        try:
            response = requests.delete(
                f"{self.BASE_URL}/rooms/{room_name}",
                headers=self._headers,
                timeout=30,
            )

            if response.status_code == 404:
                logger.info(f"Room {room_name} not found for deletion")
                return False

            response.raise_for_status()
            logger.info(f"Deleted Daily.co room: {room_name}")
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

        Daily.co uses JWT tokens for participant authentication.
        Tokens include:
        - Room name restriction
        - Participant identity
        - Expiration time
        - Permissions based on role
        """
        # Use timezone-aware UTC datetime for correct timestamp calculation
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        exp_timestamp = int(expires_at.timestamp())

        # Token configuration per Daily.co API docs
        # https://docs.daily.co/reference/rest-api/meeting-tokens
        token_config = {
            "properties": {
                "room_name": room_name,
                "user_id": str(participant_id),
                "user_name": participant_name,
                "is_owner": participant_role == ParticipantRole.INSTRUCTOR,
                "enable_screenshare": True,
                "start_video_off": False,
                "start_audio_off": False,
                "exp": exp_timestamp,  # Expiration must be inside properties
            }
        }

        try:
            logger.info(f"Creating meeting token for room {room_name}, config: {token_config}")
            response = requests.post(
                f"{self.BASE_URL}/meeting-tokens",
                json=token_config,
                headers=self._headers,
                timeout=30,
            )

            if response.status_code != 200:
                logger.error(f"Daily.co token creation failed: status={response.status_code}, response={response.text}")
                raise TokenCreationError(f"Daily.co API error ({response.status_code}): {response.text}")

            data = response.json()

            room_url = f"https://{self.domain}/{room_name}?t={data['token']}"

            logger.info(
                f"Created meeting token for {participant_name} "
                f"(role: {participant_role.value}) in room {room_name}"
            )

            return RoomToken(
                token=data["token"],
                room_url=room_url,
                expires_at=expires_at,
                participant_id=participant_id,
                participant_role=participant_role,
                participant_name=participant_name,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create token for room {room_name}: {e}")
            raise TokenCreationError(f"Failed to create meeting token: {str(e)}")

    def is_room_active(self, room_name: str) -> bool:
        """Check if a room has active participants."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/rooms/{room_name}/presence",
                headers=self._headers,
                timeout=30,
            )

            if response.status_code == 404:
                return False

            response.raise_for_status()
            data = response.json()

            # Check if there are any participants
            return data.get("total_count", 0) > 0

        except requests.exceptions.RequestException:
            return False
