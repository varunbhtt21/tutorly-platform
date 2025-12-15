"""Message attachment domain entity."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class MessageAttachment:
    """
    Message attachment entity.

    Represents a file attachment on a message.
    """

    # Identity
    id: Optional[int] = None

    # Relationships
    message_id: int = field(default=0)

    # File information
    file_name: str = field(default="")
    file_url: str = field(default="")
    file_type: str = field(default="")  # MIME type
    file_size: int = field(default=0)  # Size in bytes

    # Timestamps
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize domain invariants."""
        if not self.message_id:
            raise ValueError("Message ID is required")
        if not self.file_name:
            raise ValueError("File name is required")
        if not self.file_url:
            raise ValueError("File URL is required")

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        message_id: int,
        file_name: str,
        file_url: str,
        file_type: str,
        file_size: int,
    ) -> "MessageAttachment":
        """
        Create a new attachment.

        Args:
            message_id: ID of the message
            file_name: Original file name
            file_url: URL where file is stored
            file_type: MIME type
            file_size: Size in bytes

        Returns:
            New MessageAttachment instance
        """
        return cls(
            message_id=message_id,
            file_name=file_name,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size,
            created_at=datetime.utcnow(),
        )

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def is_image(self) -> bool:
        """Check if attachment is an image."""
        return self.file_type.startswith("image/")

    @property
    def file_size_formatted(self) -> str:
        """Get human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """Attachment equality based on ID."""
        if not isinstance(other, MessageAttachment):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make MessageAttachment hashable."""
        return hash(self.id) if self.id else hash(id(self))
