"""Mapper for UploadedFile entity and SQLAlchemy UploadedFile model."""

from typing import Dict, Any

from app.domains.file.entities import UploadedFile as DomainUploadedFile
from app.domains.file.value_objects import FileType, FileStatus
from app.infrastructure.persistence.sqlalchemy_models import (
    UploadedFile as SQLAlchemyUploadedFile,
    FileType as SQLAlchemyFileType,
    FileStatus as SQLAlchemyFileStatus,
)


class FileMapper:
    """
    Maps between domain UploadedFile entity and SQLAlchemy UploadedFile model.

    Handles conversion of FileType and FileStatus enums.
    """

    @staticmethod
    def to_domain(db_file: SQLAlchemyUploadedFile) -> DomainUploadedFile:
        """
        Convert SQLAlchemy UploadedFile to domain UploadedFile entity.

        Args:
            db_file: SQLAlchemy UploadedFile model instance

        Returns:
            Domain UploadedFile entity
        """
        if db_file is None:
            return None

        return DomainUploadedFile(
            id=str(db_file.id),
            user_id=str(db_file.uploaded_by),
            instructor_id=str(db_file.instructor_id) if db_file.instructor_id else None,
            student_id=str(db_file.student_id) if db_file.student_id else None,
            original_filename=db_file.original_filename,
            stored_filename=db_file.stored_filename,
            file_path=db_file.file_path,
            file_type=FileType(db_file.file_type.value),
            status=FileStatus(db_file.status.value),
            mime_type=db_file.mime_type,
            file_size=db_file.file_size,
            storage_backend=db_file.storage_backend,
            public_url=db_file.public_url,
            is_optimized=db_file.is_optimized,
            thumbnail_url=db_file.thumbnail_path,
            created_at=db_file.created_at,
            updated_at=db_file.updated_at,
        )

    @staticmethod
    def to_persistence(domain_file: DomainUploadedFile) -> Dict[str, Any]:
        """
        Convert domain UploadedFile entity to dict for SQLAlchemy update.

        Args:
            domain_file: Domain UploadedFile entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        return {
            "uploaded_by": int(domain_file.user_id),
            "instructor_id": int(domain_file.instructor_id) if domain_file.instructor_id else None,
            "student_id": int(domain_file.student_id) if domain_file.student_id else None,
            "original_filename": domain_file.original_filename,
            "stored_filename": domain_file.stored_filename,
            "file_path": domain_file.file_path,
            "file_type": domain_file.file_type.value,
            "status": domain_file.status.value,
            "mime_type": domain_file.mime_type,
            "file_size": domain_file.file_size,
            "storage_backend": domain_file.storage_backend,
            "public_url": domain_file.public_url,
            "is_optimized": domain_file.is_optimized,
            "thumbnail_path": domain_file.thumbnail_url,
            "updated_at": domain_file.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_file: DomainUploadedFile) -> SQLAlchemyUploadedFile:
        """
        Create new SQLAlchemy UploadedFile instance from domain UploadedFile.

        Args:
            domain_file: Domain UploadedFile entity

        Returns:
            SQLAlchemy UploadedFile model instance
        """
        return SQLAlchemyUploadedFile(
            uploaded_by=int(domain_file.user_id),
            instructor_id=int(domain_file.instructor_id) if domain_file.instructor_id else None,
            student_id=int(domain_file.student_id) if domain_file.student_id else None,
            original_filename=domain_file.original_filename,
            stored_filename=domain_file.stored_filename,
            file_path=domain_file.file_path,
            file_type=domain_file.file_type.value,
            status=domain_file.status.value,
            mime_type=domain_file.mime_type,
            file_size=domain_file.file_size,
            storage_backend=domain_file.storage_backend,
            public_url=domain_file.public_url,
            is_optimized=domain_file.is_optimized,
            thumbnail_path=domain_file.thumbnail_url,
        )

    @staticmethod
    def update_orm_instance(
        db_file: SQLAlchemyUploadedFile,
        domain_file: DomainUploadedFile
    ) -> None:
        """
        Update SQLAlchemy UploadedFile instance from domain UploadedFile.

        Args:
            db_file: SQLAlchemy UploadedFile model instance to update
            domain_file: Domain UploadedFile entity with new values
        """
        db_file.file_path = domain_file.file_path
        db_file.status = domain_file.status.value
        db_file.public_url = domain_file.public_url
        db_file.is_optimized = domain_file.is_optimized
        db_file.thumbnail_path = domain_file.thumbnail_url
        db_file.updated_at = domain_file.updated_at
