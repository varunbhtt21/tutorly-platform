from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..value_objects import FileStatus, FileType


@dataclass
class UploadedFile:
    """Domain entity representing an uploaded file in the system."""

    id: str
    user_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: FileType
    status: FileStatus
    mime_type: str
    file_size: int
    storage_backend: str
    created_at: datetime
    updated_at: datetime
    instructor_id: Optional[str] = None
    student_id: Optional[str] = None
    public_url: Optional[str] = None
    is_optimized: bool = False
    thumbnail_url: Optional[str] = None

    @staticmethod
    def create(
        user_id: str,
        filename: str,
        file_type: FileType,
        mime_type: str,
        file_size: int,
        storage_backend: str,
        instructor_id: Optional[str] = None,
        student_id: Optional[str] = None,
    ) -> "UploadedFile":
        """Factory method to create a new uploaded file entity.

        Args:
            user_id: ID of the user uploading the file
            filename: Original filename
            file_type: Type of file being uploaded
            mime_type: MIME type of the file
            file_size: Size of file in bytes
            storage_backend: Storage backend being used (e.g., 's3', 'gcs')
            instructor_id: Optional ID if file belongs to an instructor
            student_id: Optional ID if file belongs to a student

        Returns:
            UploadedFile: New file entity in UPLOADING status
        """
        now = datetime.utcnow()
        stored_filename = f"{uuid4()}_{filename}"
        file_path = f"uploads/{user_id}/{file_type.value}/{stored_filename}"

        return UploadedFile(
            id=str(uuid4()),
            user_id=user_id,
            instructor_id=instructor_id,
            student_id=student_id,
            original_filename=filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file_type,
            status=FileStatus.UPLOADING,
            mime_type=mime_type,
            file_size=file_size,
            storage_backend=storage_backend,
            created_at=now,
            updated_at=now,
        )

    def mark_completed(self, file_path: str, public_url: str) -> None:
        """Mark the file as successfully uploaded and completed.

        Args:
            file_path: Final path where file is stored
            public_url: Public URL to access the file
        """
        self.status = FileStatus.COMPLETED
        self.file_path = file_path
        self.public_url = public_url
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: Optional[str] = None) -> None:
        """Mark the file upload as failed.

        Args:
            error: Optional error message explaining the failure
        """
        self.status = FileStatus.FAILED
        self.updated_at = datetime.utcnow()

    def mark_deleted(self) -> None:
        """Mark the file as deleted."""
        self.status = FileStatus.DELETED
        self.updated_at = datetime.utcnow()

    def mark_optimized(self, thumbnail_url: Optional[str] = None) -> None:
        """Mark the file as optimized (e.g., after image/video processing).

        Args:
            thumbnail_url: Optional URL to a thumbnail for media files
        """
        self.is_optimized = True
        self.thumbnail_url = thumbnail_url
        self.updated_at = datetime.utcnow()

    @property
    def is_image(self) -> bool:
        """Check if this file is an image."""
        return self.file_type.is_image

    @property
    def is_video(self) -> bool:
        """Check if this file is a video."""
        return self.file_type.is_video

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
