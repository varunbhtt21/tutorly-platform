"""IntroVideoUpdated domain event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IntroVideoUpdated:
    """
    Domain event: Instructor introduction video has been updated.

    Emitted when an instructor uploads or changes their introduction video.
    Can trigger:
    - Update instructor video in search index
    - Generate video thumbnail
    - Invalidate cached video data
    - Trigger re-verification if instructor is already verified
    - Send confirmation email to instructor
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    video_url: str
    updated_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"IntroVideoUpdated(instructor_id={self.instructor_id})"
