"""Use case for listing files uploaded by a user."""

from typing import List, Optional

from app.domains.file.entities import UploadedFile
from app.domains.file.repositories import IFileRepository
from app.domains.file.value_objects import FileType


class ListUserFilesUseCase:
    """
    Use case for listing files uploaded by a specific user.

    Retrieves all files owned by a user with optional filtering by file type.
    """

    def __init__(self, file_repo: IFileRepository):
        """
        Initialize ListUserFilesUseCase.

        Args:
            file_repo: Repository for file persistence
        """
        self.file_repo = file_repo

    def execute(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UploadedFile]:
        """
        Execute the use case to list user's files.

        Args:
            user_id: ID of the user whose files to retrieve
            file_type: Optional filter by file type
            limit: Maximum number of results to return (default 100)
            offset: Number of results to skip for pagination (default 0)

        Returns:
            List of UploadedFile entities owned by the user

        Raises:
            ValueError: If user_id is empty or invalid
            RepositoryError: If database operation fails
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")

        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        if offset < 0:
            raise ValueError("offset must be non-negative")

        # Retrieve files from repository with optional type filter
        files = self.file_repo.get_by_user(
            user_id=user_id,
            file_type=file_type,
            limit=limit,
            offset=offset,
        )

        return files
