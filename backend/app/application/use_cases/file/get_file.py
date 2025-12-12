"""Use case for retrieving a single file from the platform."""

from app.domains.file.entities import UploadedFile
from app.domains.file.repositories import IFileRepository


class GetFileUseCase:
    """
    Use case for retrieving a single file from the platform.

    Retrieves a file by ID after verifying that the requesting user
    owns or has permission to access the file.
    """

    def __init__(self, file_repo: IFileRepository):
        """
        Initialize GetFileUseCase.

        Args:
            file_repo: Repository for file persistence
        """
        self.file_repo = file_repo

    def execute(self, file_id: str, user_id: str) -> UploadedFile:
        """
        Execute the use case to retrieve a file.

        Args:
            file_id: ID of the file to retrieve
            user_id: ID of the user requesting the file (must own the file)

        Returns:
            UploadedFile entity

        Raises:
            ValueError: If file doesn't exist or user doesn't own the file
            RepositoryError: If database operation fails
        """
        # Retrieve the file from repository
        file = self.file_repo.get_by_id(file_id)

        if not file:
            raise ValueError(f"File with ID '{file_id}' not found")

        # Verify ownership
        if file.user_id != user_id:
            raise ValueError(
                f"User '{user_id}' does not have permission to access file '{file_id}'"
            )

        return file
