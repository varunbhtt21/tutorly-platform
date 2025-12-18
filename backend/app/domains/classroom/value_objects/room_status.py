"""
Room Status Value Object.

Represents the lifecycle status of a video classroom room.
"""

from enum import Enum


class RoomStatus(str, Enum):
    """
    Status of a video classroom room.

    Lifecycle:
    PENDING -> CREATED -> ACTIVE -> ENDED
                       -> EXPIRED (if not joined before expiry)
    """

    PENDING = "pending"      # Room creation requested but not yet created
    CREATED = "created"      # Room created with provider, waiting for participants
    ACTIVE = "active"        # Session in progress (participants joined)
    ENDED = "ended"          # Session completed normally
    EXPIRED = "expired"      # Room expired without proper ending
    FAILED = "failed"        # Room creation or session failed
