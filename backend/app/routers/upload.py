"""
File Upload Router - Pure DDD Implementation.

API endpoints for file uploads (photos, videos, documents) using Pure DDD principles:
- Thin controllers: Only handle HTTP concerns
- Delegate business logic to use cases
- Use domain entities and value objects
- Proper file validation and optimization
"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.domains.user.entities import User
from app.domains.file.entities import UploadedFile
from app.domains.file.value_objects import FileType, FileStatus
from app.core.dependencies import (
    get_current_user,
    get_current_user_allow_inactive,
    get_upload_file_use_case,
    get_delete_file_use_case,
    get_get_file_use_case,
    get_list_user_files_use_case,
)
from app.application.use_cases.file import (
    UploadFileUseCase,
    DeleteFileUseCase,
    GetFileUseCase,
    ListUserFilesUseCase,
)

# For file processing
import os
from pathlib import Path
from PIL import Image
import io


# ============================================================================
# Request/Response DTOs (Inline Pydantic Models)
# ============================================================================


class FileUploadResponse(BaseModel):
    """File upload response."""
    id: str
    user_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: FileType
    status: FileStatus
    mime_type: str
    file_size: int
    public_url: Optional[str]
    thumbnail_url: Optional[str]
    is_optimized: bool

    @classmethod
    def from_domain(cls, file: UploadedFile) -> "FileUploadResponse":
        """Create response from domain entity."""
        return cls(
            id=file.id,
            user_id=file.user_id,
            original_filename=file.original_filename,
            stored_filename=file.stored_filename,
            file_path=file.file_path,
            file_type=file.file_type,
            status=file.status,
            mime_type=file.mime_type,
            file_size=file.file_size,
            public_url=file.public_url,
            thumbnail_url=file.thumbnail_url,
            is_optimized=file.is_optimized,
        )


class FileMetadataResponse(BaseModel):
    """Detailed file metadata response."""
    id: str
    user_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: FileType
    status: FileStatus
    mime_type: str
    file_size: int
    public_url: Optional[str]
    thumbnail_url: Optional[str]
    is_optimized: bool
    instructor_id: Optional[str]
    student_id: Optional[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, file: UploadedFile) -> "FileMetadataResponse":
        """Create response from domain entity."""
        return cls(
            id=file.id,
            user_id=file.user_id,
            original_filename=file.original_filename,
            stored_filename=file.stored_filename,
            file_path=file.file_path,
            file_type=file.file_type,
            status=file.status,
            mime_type=file.mime_type,
            file_size=file.file_size,
            public_url=file.public_url,
            thumbnail_url=file.thumbnail_url,
            is_optimized=file.is_optimized,
            instructor_id=file.instructor_id,
            student_id=file.student_id,
            created_at=file.created_at.isoformat(),
            updated_at=file.updated_at.isoformat(),
        )


class FileDeleteResponse(BaseModel):
    """File deletion response."""
    success: bool
    message: str
    file_id: str


class FileListResponse(BaseModel):
    """List of files response."""
    files: list[FileUploadResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Create router
router = APIRouter()


# ============================================================================
# File Validation Constants
# ============================================================================

# File size limits (in bytes)
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20MB

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


# ============================================================================
# Helper Functions
# ============================================================================


def handle_domain_exception(e: Exception) -> None:
    """
    Convert domain exceptions to HTTP exceptions.

    Args:
        e: Exception from domain or use case layer

    Raises:
        HTTPException: Appropriate HTTP exception
    """
    error_message = str(e)

    if "not found" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": error_message},
        )
    elif "invalid file type" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_FILE_TYPE", "message": error_message},
        )
    elif "file size" in error_message.lower() or "too large" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": error_message},
        )
    elif "permission" in error_message.lower() or "forbidden" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "FORBIDDEN", "message": error_message},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
        )


def validate_file_type(file: UploadFile, allowed_types: set) -> None:
    """
    Validate file MIME type.

    Args:
        file: Uploaded file
        allowed_types: Set of allowed MIME types

    Raises:
        HTTPException: If file type is not allowed
    """
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_FILE_TYPE",
                "message": f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}",
            },
        )


def validate_file_size(file_size: int, max_size: int) -> None:
    """
    Validate file size.

    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes

    Raises:
        HTTPException: If file is too large
    """
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": f"File too large. Maximum size: {max_mb}MB",
            },
        )


async def optimize_image(file: UploadFile, max_width: int = 1920, quality: int = 85) -> bytes:
    """
    Optimize image file.

    Args:
        file: Uploaded image file
        max_width: Maximum width in pixels
        quality: JPEG quality (1-100)

    Returns:
        Optimized image bytes
    """
    try:
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer

        # Open image
        img = Image.open(io.BytesIO(content))

        # Convert RGBA to RGB if needed
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        # Resize if too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save optimized image
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "IMAGE_PROCESSING_ERROR", "message": f"Failed to process image: {str(e)}"},
        )


async def create_thumbnail(file: UploadFile, size: tuple = (200, 200)) -> bytes:
    """
    Create thumbnail from image.

    Args:
        file: Uploaded image file
        size: Thumbnail size (width, height)

    Returns:
        Thumbnail image bytes
    """
    try:
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer

        # Open image
        img = Image.open(io.BytesIO(content))

        # Convert RGBA to RGB if needed
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save thumbnail
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()

    except Exception as e:
        # If thumbnail creation fails, it's not critical
        return None


def save_file_to_storage(file_bytes: bytes, file_path: str) -> str:
    """
    Save file to local storage.

    Args:
        file_bytes: File content
        file_path: Relative file path

    Returns:
        Public URL to the file
    """
    try:
        # Create directory structure
        full_path = Path("storage") / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, "wb") as f:
            f.write(file_bytes)

        # Return public URL (in production, this would be a CDN URL)
        return f"/storage/{file_path}"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "STORAGE_ERROR", "message": f"Failed to save file: {str(e)}"},
        )


def delete_file_from_storage(file_path: str) -> None:
    """
    Delete file from local storage.

    Args:
        file_path: Relative file path
    """
    try:
        full_path = Path("storage") / file_path
        if full_path.exists():
            full_path.unlink()
    except Exception:
        # Silent failure for file deletion
        pass


# ============================================================================
# File Upload Endpoints
# ============================================================================


@router.post(
    "/photo",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload profile photo",
    description="Upload and optimize a profile photo. Creates main photo and thumbnail.",
)
async def upload_profile_photo(
    file: UploadFile = File(..., description="Image file to upload"),
    optimize: bool = Query(True, description="Whether to optimize the image"),
    create_thumbnail_flag: bool = Query(True, description="Whether to create thumbnail"),
    current_user: User = Depends(get_current_user_allow_inactive),
    upload_use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
) -> FileUploadResponse:
    """
    Upload profile photo.

    - Validates file type and size
    - Optimizes image if requested
    - Creates thumbnail if requested
    - Stores in appropriate directory based on user type
    """
    try:
        # Validate file type
        validate_file_type(file, ALLOWED_IMAGE_TYPES)

        # Read file content to get size
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer

        # Validate file size
        validate_file_size(file_size, MAX_PHOTO_SIZE)

        # Determine instructor_id or student_id
        instructor_id = None
        student_id = None
        if current_user.is_instructor:
            # Would need to query instructor profile here
            pass
        elif current_user.is_student:
            # Would need to query student profile here
            pass

        # Create file entity using use case
        uploaded_file = upload_use_case.execute(
            user_id=str(current_user.id),
            filename=file.filename,
            file_type_str="profile_photo",
            mime_type=file.content_type,
            file_size=file_size,
            storage_backend="local",
            instructor_id=str(instructor_id) if instructor_id else None,
            student_id=str(student_id) if student_id else None,
        )

        # Process image
        if optimize:
            file_bytes = await optimize_image(file)
            uploaded_file.is_optimized = True
        else:
            file_bytes = content

        # Save main file
        public_url = save_file_to_storage(file_bytes, uploaded_file.file_path)
        uploaded_file.mark_completed(uploaded_file.file_path, public_url)

        # Create thumbnail if requested
        if create_thumbnail_flag:
            thumbnail_bytes = await create_thumbnail(file)
            if thumbnail_bytes:
                thumbnail_path = uploaded_file.file_path.replace(uploaded_file.stored_filename, f"thumb_{uploaded_file.stored_filename}")
                thumbnail_url = save_file_to_storage(thumbnail_bytes, thumbnail_path)
                uploaded_file.thumbnail_url = thumbnail_url

        return FileUploadResponse.from_domain(uploaded_file)

    except HTTPException:
        raise
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/video",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload intro video",
    description="Upload an introduction video (for instructors).",
)
async def upload_intro_video(
    file: UploadFile = File(..., description="Video file to upload"),
    generate_thumbnail: bool = Query(False, description="Whether to generate video thumbnail"),
    current_user: User = Depends(get_current_user_allow_inactive),
    upload_use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
) -> FileUploadResponse:
    """
    Upload introduction video.

    - Validates file type and size
    - Stores video file
    - Optionally generates thumbnail (not implemented yet)
    """
    try:
        # Validate file type
        validate_file_type(file, ALLOWED_VIDEO_TYPES)

        # Read file content to get size
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer

        # Validate file size
        validate_file_size(file_size, MAX_VIDEO_SIZE)

        # Determine instructor_id
        instructor_id = None
        if current_user.is_instructor:
            # Would need to query instructor profile here
            pass

        # Create file entity using use case
        uploaded_file = upload_use_case.execute(
            user_id=str(current_user.id),
            filename=file.filename,
            file_type_str="intro_video",
            mime_type=file.content_type,
            file_size=file_size,
            storage_backend="local",
            instructor_id=str(instructor_id) if instructor_id else None,
            student_id=None,
        )

        # Save video file
        public_url = save_file_to_storage(content, uploaded_file.file_path)
        uploaded_file.mark_completed(uploaded_file.file_path, public_url)

        # TODO: Generate video thumbnail if requested
        # This would require ffmpeg or similar video processing tool

        return FileUploadResponse.from_domain(uploaded_file)

    except HTTPException:
        raise
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/document",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
    description="Upload a document (certificate, diploma, etc.).",
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload (PDF or image)"),
    document_type: str = Query("certificate", description="Type of document"),
    current_user: User = Depends(get_current_user),
    upload_use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
) -> FileUploadResponse:
    """
    Upload document.

    - Validates file type and size
    - Optimizes if document is an image
    - Stores in appropriate directory
    """
    try:
        # Validate file type
        validate_file_type(file, ALLOWED_DOCUMENT_TYPES)

        # Read file content to get size
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer

        # Validate file size
        validate_file_size(file_size, MAX_DOCUMENT_SIZE)

        # Determine instructor_id
        instructor_id = None
        if current_user.is_instructor:
            # Would need to query instructor profile here
            pass

        # Create file entity using use case
        uploaded_file = upload_use_case.execute(
            user_id=str(current_user.id),
            filename=file.filename,
            file_type_str="document",
            mime_type=file.content_type,
            file_size=file_size,
            storage_backend="local",
            instructor_id=str(instructor_id) if instructor_id else None,
            student_id=None,
        )

        # Optimize if image
        if file.content_type in ALLOWED_IMAGE_TYPES:
            file_bytes = await optimize_image(file, max_width=2048, quality=90)
            uploaded_file.is_optimized = True
        else:
            file_bytes = content

        # Save file
        public_url = save_file_to_storage(file_bytes, uploaded_file.file_path)
        uploaded_file.mark_completed(uploaded_file.file_path, public_url)

        return FileUploadResponse.from_domain(uploaded_file)

    except HTTPException:
        raise
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# File Management Endpoints
# ============================================================================


@router.delete(
    "/{file_id}",
    response_model=FileDeleteResponse,
    summary="Delete file",
    description="Delete an uploaded file from storage and database.",
)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    delete_use_case: DeleteFileUseCase = Depends(get_delete_file_use_case),
    get_file_use_case: GetFileUseCase = Depends(get_get_file_use_case),
) -> FileDeleteResponse:
    """
    Delete file.

    - Removes file from storage
    - Removes thumbnail if exists
    - Removes database record
    - Only file owner can delete
    """
    try:
        # Get file to verify ownership and get paths
        file = get_file_use_case.execute(file_id=file_id, user_id=str(current_user.id))

        # Delete from storage
        delete_file_from_storage(file.file_path)
        if file.thumbnail_url:
            # Extract path from thumbnail URL and delete
            thumbnail_path = file.thumbnail_url.replace("/storage/", "")
            delete_file_from_storage(thumbnail_path)

        # Delete from database
        delete_use_case.execute(file_id=file_id, user_id=str(current_user.id))

        return FileDeleteResponse(
            success=True,
            message="File deleted successfully",
            file_id=file_id,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "/{file_id}",
    response_model=FileMetadataResponse,
    summary="Get file metadata",
    description="Get detailed metadata for an uploaded file.",
)
async def get_file_metadata(
    file_id: str,
    current_user: User = Depends(get_current_user),
    get_file_use_case: GetFileUseCase = Depends(get_get_file_use_case),
) -> FileMetadataResponse:
    """
    Get file metadata.

    Returns detailed information about an uploaded file.
    Only file owner can access metadata.
    """
    try:
        file = get_file_use_case.execute(file_id=file_id, user_id=str(current_user.id))

        return FileMetadataResponse.from_domain(file)

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "",
    response_model=FileListResponse,
    summary="List user files",
    description="Get list of files uploaded by the current user.",
)
async def list_user_files(
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    current_user: User = Depends(get_current_user),
    list_files_use_case: ListUserFilesUseCase = Depends(get_list_user_files_use_case),
) -> FileListResponse:
    """
    List user files.

    Returns list of all files uploaded by the current user.
    Optionally filter by file type.
    """
    try:
        # Execute use case
        files = list_files_use_case.execute(
            user_id=str(current_user.id),
            file_type=file_type,
        )

        return FileListResponse(
            files=[FileUploadResponse.from_domain(f) for f in files],
            total=len(files),
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "/storage/usage",
    summary="Get storage usage",
    description="Get total storage used by the current user in bytes.",
)
async def get_storage_usage(
    current_user: User = Depends(get_current_user),
    list_files_use_case: ListUserFilesUseCase = Depends(get_list_user_files_use_case),
) -> dict:
    """
    Get storage usage.

    Returns total storage used by the current user.
    """
    try:
        # Get all files
        files = list_files_use_case.execute(
            user_id=str(current_user.id),
            file_type=None,
        )

        # Calculate total size
        total_bytes = sum(f.file_size for f in files)

        return {
            "user_id": str(current_user.id),
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "total_gb": round(total_bytes / (1024 * 1024 * 1024), 4),
        }

    except Exception as e:
        handle_domain_exception(e)
