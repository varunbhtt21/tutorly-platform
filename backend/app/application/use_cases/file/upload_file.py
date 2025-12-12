"""Use case for uploading files to the platform."""

from typing import Optional

from app.domains.file.entities import UploadedFile
from app.domains.file.repositories import IFileRepository
from app.domains.file.value_objects import FileType


class UploadFileUseCase:
    """
    Use case for uploading a file to the platform.

    Handles the creation of a new file upload entity with proper metadata
    and storage configuration. The file is created in UPLOADING status and
    transitioned to COMPLETED once the actual file is stored.
    """

    def __init__(self, file_repo: IFileRepository):
        """
        Initialize UploadFileUseCase.

        Args:
            file_repo: Repository for file persistence
        """
        self.file_repo = file_repo

    def execute(
        self,
        user_id: str,
        filename: str,
        file_type_str: str,
        mime_type: str,
        file_size: int,
        storage_backend: str,
        instructor_id: Optional[str] = None,
        student_id: Optional[str] = None,
    ) -> UploadedFile:
        """
        Execute the use case to upload a file.

        Args:
            user_id: User ID who is uploading the file
            filename: Original filename
            file_type_str: File type as string (e.g., "profile_photo", "intro_video")
            mime_type: MIME type of the file
            file_size: Size of the file in bytes
            storage_backend: Storage backend to use (e.g., "local", "s3")
            instructor_id: Optional ID if file belongs to an instructor profile
            student_id: Optional ID if file belongs to a student profile

        Returns:
            Created UploadedFile entity with initial metadata

        Raises:
            ValueError: If file type is invalid or file size is invalid
            RepositoryError: If database operation fails
        """
        # Validate file type
        try:
            file_type = FileType(file_type_str)
        except ValueError:
            valid_types = ", ".join([ft.value for ft in FileType])
            raise ValueError(
                f"Invalid file type '{file_type_str}'. "
                f"Valid types are: {valid_types}"
            )

        # Validate file size (must be positive)
        if file_size <= 0:
            raise ValueError("File size must be greater than 0 bytes")

        # Create new file entity using factory method
        file = UploadedFile.create(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            storage_backend=storage_backend,
            instructor_id=instructor_id,
            student_id=student_id,
        )

        # Save to repository
        saved_file = self.file_repo.save(file)

        return saved_file
