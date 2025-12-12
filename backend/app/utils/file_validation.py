"""
File validation utilities.

Validates file uploads for type, size, and security.
"""

import magic
import os
from typing import Tuple, Optional
from fastapi import UploadFile

from app.core.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    FileUploadError,
)


# File size limits (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024  # 5 MB

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/mpeg",
    "video/quicktime",  # .mov
    "video/x-msvideo",  # .avi
    "video/webm",
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}

# File extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mpeg", ".webm"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (e.g., {'.jpg', '.png'})

    Returns:
        True if extension is allowed, False otherwise
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions


async def detect_mime_type(file: UploadFile) -> str:
    """
    Detect MIME type of uploaded file using python-magic.

    Args:
        file: Uploaded file

    Returns:
        Detected MIME type

    Raises:
        FileUploadError: If MIME type detection fails
    """
    try:
        # Read first 2048 bytes for magic number detection
        content = await file.read(2048)
        await file.seek(0)  # Reset file pointer

        mime = magic.from_buffer(content, mime=True)
        return mime

    except Exception as e:
        raise FileUploadError(f"Failed to detect file type: {str(e)}")


async def validate_image(file: UploadFile, max_size: int = MAX_IMAGE_SIZE) -> Tuple[bool, Optional[str]]:
    """
    Validate image file.

    Args:
        file: Uploaded image file
        max_size: Maximum file size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not validate_file_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return False, f"Invalid file extension. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > max_size:
        return False, f"File too large. Maximum size: {max_size / (1024 * 1024):.1f} MB"

    if file_size == 0:
        return False, "File is empty"

    # Detect and validate MIME type
    try:
        mime_type = await detect_mime_type(file)
        if mime_type not in ALLOWED_IMAGE_TYPES:
            return False, f"Invalid file type: {mime_type}. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
    except FileUploadError as e:
        return False, str(e)

    return True, None


async def validate_video(file: UploadFile, max_size: int = MAX_VIDEO_SIZE) -> Tuple[bool, Optional[str]]:
    """
    Validate video file.

    Args:
        file: Uploaded video file
        max_size: Maximum file size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not validate_file_extension(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        return False, f"Invalid file extension. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > max_size:
        return False, f"File too large. Maximum size: {max_size / (1024 * 1024):.1f} MB"

    if file_size == 0:
        return False, "File is empty"

    # Detect and validate MIME type
    try:
        mime_type = await detect_mime_type(file)
        if mime_type not in ALLOWED_VIDEO_TYPES:
            return False, f"Invalid file type: {mime_type}. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
    except FileUploadError as e:
        return False, str(e)

    return True, None


async def validate_document(file: UploadFile, max_size: int = MAX_DOCUMENT_SIZE) -> Tuple[bool, Optional[str]]:
    """
    Validate document file (PDF or image).

    Args:
        file: Uploaded document file
        max_size: Maximum file size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not validate_file_extension(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return False, f"Invalid file extension. Allowed: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > max_size:
        return False, f"File too large. Maximum size: {max_size / (1024 * 1024):.1f} MB"

    if file_size == 0:
        return False, "File is empty"

    # Detect and validate MIME type
    try:
        mime_type = await detect_mime_type(file)
        if mime_type not in ALLOWED_DOCUMENT_TYPES:
            return False, f"Invalid file type: {mime_type}. Allowed: {', '.join(ALLOWED_DOCUMENT_TYPES)}"
    except FileUploadError as e:
        return False, str(e)

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Removes potentially dangerous characters and limits length.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Remove any characters that aren't alphanumeric, underscore, hyphen, or dot
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
    filename = "".join(c for c in filename if c in safe_chars)

    # Limit filename length (preserve extension)
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    filename = name + ext

    return filename
