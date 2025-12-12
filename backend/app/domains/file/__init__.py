"""File domain following Pure Domain-Driven Design (DDD).

This domain encapsulates all file-related business logic including:
- File upload and management
- File type and status tracking
- File storage operations
- Domain events for file lifecycle

Structure:
- value_objects: FileType, FileStatus
- entities: UploadedFile aggregate root
- events: FileUploaded, FileDeleted
- repositories: IFileRepository interface
"""

from .entities import UploadedFile
from .events import FileDeleted, FileUploaded
from .repositories import IFileRepository
from .value_objects import FileStatus, FileType

__all__ = [
    "FileType",
    "FileStatus",
    "UploadedFile",
    "FileUploaded",
    "FileDeleted",
    "IFileRepository",
]
