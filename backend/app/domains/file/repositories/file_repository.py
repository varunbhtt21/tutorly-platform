from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import UploadedFile
from ..value_objects import FileStatus, FileType


class IFileRepository(ABC):
    """Repository interface for file domain entity persistence."""

    @abstractmethod
    def save(self, file: UploadedFile) -> UploadedFile:
        """Save a file entity to the repository.

        Args:
            file: The UploadedFile entity to persist

        Returns:
            The saved UploadedFile entity with DB-generated ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, file_id: str) -> Optional[UploadedFile]:
        """Retrieve a file by its ID.

        Args:
            file_id: The unique identifier of the file

        Returns:
            UploadedFile if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_user(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
        status: Optional[FileStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UploadedFile]:
        """Retrieve files by user with optional filtering.

        Args:
            user_id: The ID of the user who owns the files
            file_type: Optional filter by file type
            status: Optional filter by file status
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of UploadedFile entities matching the criteria
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        file_type: Optional[FileType] = None,
        status: Optional[FileStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UploadedFile]:
        """Retrieve all files with optional filtering.

        Args:
            file_type: Optional filter by file type
            status: Optional filter by file status
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of UploadedFile entities matching the criteria
        """
        pass

    @abstractmethod
    async def update(self, file: UploadedFile) -> None:
        """Update an existing file entity.

        Args:
            file: The UploadedFile entity with updated values
        """
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Delete a file by its ID.

        Args:
            file_id: The unique identifier of the file to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_storage_usage(self, user_id: str) -> int:
        """Get total storage usage for a user in bytes.

        Args:
            user_id: The ID of the user

        Returns:
            Total size of all files owned by the user in bytes
        """
        pass
