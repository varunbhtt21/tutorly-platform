"""Use case for deleting files from the platform."""

from typing import Optional

from app.domains.file.repositories import IFileRepository


class DeleteFileUseCase:
    """
    Use case for deleting a file from the platform.

    Marks a file as deleted in the repository after verifying that
    the user requesting deletion owns the file.
    """

    def __init__(self, file_repo: IFileRepository):
        """
        Initialize DeleteFileUseCase.

        Args:
            file_repo: Repository for file persistence
        """
        self.file_repo = file_repo

    def execute(self, file_id: str, user_id: str) -> bool:
        """
        Execute the use case to delete a file.

        Args:
            file_id: ID of the file to delete
            user_id: ID of the user requesting deletion (must own the file)

        Returns:
            True if file was successfully deleted, False otherwise

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
                f"User '{user_id}' does not have permission to delete file '{file_id}'"
            )

        # Mark file as deleted
        file.mark_deleted()

        # Save updated file entity
        self.file_repo.update(file)

        return True
