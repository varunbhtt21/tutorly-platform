from enum import Enum


class FileStatus(str, Enum):
    """Enumeration of file upload statuses."""

    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"

    @property
    def is_completed(self) -> bool:
        """Check if the file upload is completed."""
        return self == FileStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if the file upload failed."""
        return self == FileStatus.FAILED

    @property
    def can_be_deleted(self) -> bool:
        """Check if the file can be deleted (not already deleted)."""
        return self != FileStatus.DELETED
