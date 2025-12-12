"""
Image optimization utilities.

Handles image resizing, compression, and format conversion for uploaded images.
"""

from PIL import Image
from io import BytesIO
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


# Image size configurations (width, height)
PROFILE_PHOTO_SIZE = (400, 400)  # Square profile photos
THUMBNAIL_SIZE = (150, 150)  # Small thumbnails
LARGE_SIZE = (1200, 1200)  # Large display size


class ImageOptimizer:
    """
    Image optimization utility class.

    Provides methods for resizing, compressing, and converting images
    to optimize storage and delivery performance.
    """

    @staticmethod
    def resize_image(
        image_bytes: bytes,
        target_size: Tuple[int, int],
        maintain_aspect_ratio: bool = True
    ) -> BytesIO:
        """
        Resize image to target dimensions.

        Args:
            image_bytes: Original image bytes
            target_size: Target (width, height) in pixels
            maintain_aspect_ratio: If True, maintains aspect ratio and fits within target_size

        Returns:
            BytesIO object containing resized image

        Raises:
            Exception: If image processing fails
        """
        try:
            # Open image from bytes
            image = Image.open(BytesIO(image_bytes))

            # Convert RGBA to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            if maintain_aspect_ratio:
                # Resize maintaining aspect ratio (thumbnail method)
                image.thumbnail(target_size, Image.Resampling.LANCZOS)
            else:
                # Resize to exact dimensions
                image = image.resize(target_size, Image.Resampling.LANCZOS)

            # Save to BytesIO
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            logger.info(f"Image resized to {image.size}")
            return output

        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            raise

    @staticmethod
    def compress_image(
        image_bytes: bytes,
        quality: int = 85,
        max_size_kb: Optional[int] = None
    ) -> BytesIO:
        """
        Compress image to reduce file size.

        Args:
            image_bytes: Original image bytes
            quality: JPEG quality (1-100, default 85)
            max_size_kb: Optional maximum file size in KB. Will reduce quality until target met.

        Returns:
            BytesIO object containing compressed image

        Raises:
            Exception: If image processing fails
        """
        try:
            image = Image.open(BytesIO(image_bytes))

            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            output = BytesIO()

            if max_size_kb:
                # Iteratively reduce quality until size requirement met
                current_quality = quality
                while current_quality > 20:  # Don't go below quality 20
                    output = BytesIO()
                    image.save(output, format='JPEG', quality=current_quality, optimize=True)
                    size_kb = output.tell() / 1024

                    if size_kb <= max_size_kb:
                        break

                    current_quality -= 5
                    logger.info(f"Reducing quality to {current_quality} (current size: {size_kb:.1f}KB)")

                output.seek(0)
                logger.info(f"Image compressed to {output.tell() / 1024:.1f}KB at quality {current_quality}")
            else:
                # Simple compression with specified quality
                image.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                logger.info(f"Image compressed at quality {quality}")

            return output

        except Exception as e:
            logger.error(f"Failed to compress image: {e}")
            raise

    @staticmethod
    def convert_to_webp(image_bytes: bytes, quality: int = 85) -> BytesIO:
        """
        Convert image to WebP format for better compression.

        Args:
            image_bytes: Original image bytes
            quality: WebP quality (1-100, default 85)

        Returns:
            BytesIO object containing WebP image

        Raises:
            Exception: If image processing fails
        """
        try:
            image = Image.open(BytesIO(image_bytes))

            output = BytesIO()
            image.save(output, format='WEBP', quality=quality, method=6)
            output.seek(0)

            logger.info(f"Image converted to WebP format")
            return output

        except Exception as e:
            logger.error(f"Failed to convert image to WebP: {e}")
            raise

    @staticmethod
    def create_thumbnail(image_bytes: bytes, size: Tuple[int, int] = THUMBNAIL_SIZE) -> BytesIO:
        """
        Create thumbnail from image.

        Args:
            image_bytes: Original image bytes
            size: Thumbnail size (width, height)

        Returns:
            BytesIO object containing thumbnail

        Raises:
            Exception: If image processing fails
        """
        return ImageOptimizer.resize_image(image_bytes, size, maintain_aspect_ratio=True)

    @staticmethod
    def optimize_profile_photo(image_bytes: bytes) -> Tuple[BytesIO, BytesIO]:
        """
        Optimize profile photo - create main photo and thumbnail.

        Args:
            image_bytes: Original image bytes

        Returns:
            Tuple of (optimized_photo, thumbnail)

        Raises:
            Exception: If image processing fails
        """
        try:
            # Create optimized profile photo (400x400)
            main_photo = ImageOptimizer.resize_image(
                image_bytes,
                PROFILE_PHOTO_SIZE,
                maintain_aspect_ratio=False  # Square crop for profile photos
            )

            # Create thumbnail (150x150)
            thumbnail = ImageOptimizer.create_thumbnail(image_bytes)

            logger.info("Profile photo optimized successfully")
            return main_photo, thumbnail

        except Exception as e:
            logger.error(f"Failed to optimize profile photo: {e}")
            raise

    @staticmethod
    def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
        """
        Get image dimensions without loading full image.

        Args:
            image_bytes: Image bytes

        Returns:
            Tuple of (width, height)

        Raises:
            Exception: If image processing fails
        """
        try:
            image = Image.open(BytesIO(image_bytes))
            return image.size
        except Exception as e:
            logger.error(f"Failed to get image dimensions: {e}")
            raise

    @staticmethod
    def validate_image_format(image_bytes: bytes) -> bool:
        """
        Validate if bytes represent a valid image.

        Args:
            image_bytes: Image bytes to validate

        Returns:
            True if valid image, False otherwise
        """
        try:
            image = Image.open(BytesIO(image_bytes))
            image.verify()
            return True
        except Exception:
            return False


# Convenience functions for common operations

async def optimize_uploaded_image(
    image_bytes: bytes,
    image_type: str = "profile_photo"
) -> dict:
    """
    Optimize uploaded image based on type.

    Args:
        image_bytes: Original image bytes
        image_type: Type of image ("profile_photo", "document", "general")

    Returns:
        Dictionary with optimized image data:
        {
            "main": BytesIO,
            "thumbnail": Optional[BytesIO],
            "original_size": int,
            "optimized_size": int,
            "dimensions": (width, height)
        }
    """
    try:
        original_size = len(image_bytes)
        dimensions = ImageOptimizer.get_image_dimensions(image_bytes)

        result = {
            "original_size": original_size,
            "dimensions": dimensions,
        }

        if image_type == "profile_photo":
            # Create square profile photo and thumbnail
            main_photo, thumbnail = ImageOptimizer.optimize_profile_photo(image_bytes)
            result["main"] = main_photo
            result["thumbnail"] = thumbnail
            result["optimized_size"] = main_photo.tell()

        elif image_type == "document":
            # Compress document image
            main = ImageOptimizer.compress_image(image_bytes, quality=90, max_size_kb=2048)
            result["main"] = main
            result["thumbnail"] = None
            result["optimized_size"] = main.tell()

        else:
            # General image optimization
            main = ImageOptimizer.compress_image(image_bytes, quality=85)
            thumbnail = ImageOptimizer.create_thumbnail(image_bytes)
            result["main"] = main
            result["thumbnail"] = thumbnail
            result["optimized_size"] = main.tell()

        logger.info(
            f"Image optimized: {original_size / 1024:.1f}KB -> "
            f"{result['optimized_size'] / 1024:.1f}KB "
            f"({(1 - result['optimized_size'] / original_size) * 100:.1f}% reduction)"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to optimize uploaded image: {e}")
        raise
