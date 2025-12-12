"""File domain events."""

from .file_deleted import FileDeleted
from .file_uploaded import FileUploaded

__all__ = ["FileUploaded", "FileDeleted"]
