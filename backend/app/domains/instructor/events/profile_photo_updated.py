"""ProfilePhotoUpdated domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProfilePhotoUpdated:
    """
    Domain event: Instructor profile photo has been updated.

    Emitted when an instructor uploads or changes their profile photo.
    Can trigger:
    - Update instructor photo in search index
    - Invalidate cached profile images
    - Trigger re-verification if instructor is already verified
    - Send confirmation email to instructor
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    photo_url: str
    updated_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"ProfilePhotoUpdated(instructor_id={self.instructor_id})"
