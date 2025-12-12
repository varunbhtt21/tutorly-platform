"""SQLAlchemy implementation of File repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from app.domains.file.entities import UploadedFile
from app.domains.file.value_objects import FileType, FileStatus
from app.domains.file.repositories import IFileRepository
from app.infrastructure.persistence.mappers import FileMapper
from app.infrastructure.persistence.sqlalchemy_models import UploadedFile as SQLAlchemyUploadedFile


class SQLAlchemyFileRepository(IFileRepository):
    """
    SQLAlchemy implementation of IFileRepository.

    Note: Interface is async but implementation is sync for now.
    Can be converted to async in the future if needed.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = FileMapper

    def save(self, file: UploadedFile) -> UploadedFile:
        """Save file to database and return the saved entity with DB-generated ID."""
        try:
            db_file = self.mapper.create_orm_instance(file)
            self.db.add(db_file)
            self.db.flush()
            self.db.commit()

            # Update the file entity with the DB-generated ID
            file.id = str(db_file.id)
            return file

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save file: {str(e)}")

    async def get_by_id(self, file_id: str) -> Optional[UploadedFile]:
        """Get file by ID."""
        try:
            db_file = self.db.query(SQLAlchemyUploadedFile).filter(
                SQLAlchemyUploadedFile.id == int(file_id)
            ).first()

            return self.mapper.to_domain(db_file) if db_file else None

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get file by ID: {str(e)}")

    async def get_by_user(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
        status: Optional[FileStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UploadedFile]:
        """Get files by user with optional filtering."""
        try:
            query = self.db.query(SQLAlchemyUploadedFile).filter(
                SQLAlchemyUploadedFile.uploaded_by == int(user_id)
            )

            if file_type:
                query = query.filter(SQLAlchemyUploadedFile.file_type == file_type.value)

            if status:
                query = query.filter(SQLAlchemyUploadedFile.status == status.value)

            db_files = query.offset(offset).limit(limit).all()

            return [self.mapper.to_domain(db_file) for db_file in db_files]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get files by user: {str(e)}")

    async def get_all(
        self,
        file_type: Optional[FileType] = None,
        status: Optional[FileStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UploadedFile]:
        """Get all files with optional filtering."""
        try:
            query = self.db.query(SQLAlchemyUploadedFile)

            if file_type:
                query = query.filter(SQLAlchemyUploadedFile.file_type == file_type.value)

            if status:
                query = query.filter(SQLAlchemyUploadedFile.status == status.value)

            db_files = query.offset(offset).limit(limit).all()

            return [self.mapper.to_domain(db_file) for db_file in db_files]

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get all files: {str(e)}")

    async def update(self, file: UploadedFile) -> None:
        """Update existing file."""
        try:
            db_file = self.db.query(SQLAlchemyUploadedFile).filter(
                SQLAlchemyUploadedFile.id == int(file.id)
            ).first()

            if not db_file:
                raise ValueError(f"File with ID {file.id} not found")

            self.mapper.update_orm_instance(db_file, file)
            self.db.flush()

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update file: {str(e)}")

    async def delete(self, file_id: str) -> bool:
        """Delete file."""
        try:
            db_file = self.db.query(SQLAlchemyUploadedFile).filter(
                SQLAlchemyUploadedFile.id == int(file_id)
            ).first()

            if not db_file:
                return False

            self.db.delete(db_file)
            self.db.flush()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete file: {str(e)}")

    async def get_storage_usage(self, user_id: str) -> int:
        """Get total storage usage for user in bytes."""
        try:
            result = self.db.query(func.sum(SQLAlchemyUploadedFile.file_size)).filter(
                SQLAlchemyUploadedFile.uploaded_by == int(user_id)
            ).scalar()

            return int(result) if result else 0

        except SQLAlchemyError as e:
            raise Exception(f"Failed to get storage usage: {str(e)}")
