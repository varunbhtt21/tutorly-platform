from enum import Enum


class FileType(str, Enum):
    """Enumeration of supported file types in the system."""

    PROFILE_PHOTO = "profile_photo"
    INTRO_VIDEO = "intro_video"
    CERTIFICATE = "certificate"
    DOCUMENT = "document"

    @property
    def is_image(self) -> bool:
        """Check if this file type is an image."""
        return self in (FileType.PROFILE_PHOTO,)

    @property
    def is_video(self) -> bool:
        """Check if this file type is a video."""
        return self in (FileType.INTRO_VIDEO,)

    @property
    def is_document(self) -> bool:
        """Check if this file type is a document."""
        return self in (FileType.CERTIFICATE, FileType.DOCUMENT)
