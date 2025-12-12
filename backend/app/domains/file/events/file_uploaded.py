from dataclasses import dataclass
from datetime import datetime

from ..value_objects import FileType


@dataclass
class FileUploaded:
    """Domain event fired when a file is successfully uploaded."""

    file_id: str
    user_id: str
    file_type: FileType
    file_size: int
    uploaded_at: datetime

    def __init__(
        self,
        file_id: str,
        user_id: str,
        file_type: FileType,
        file_size: int,
        uploaded_at: datetime,
    ) -> None:
        self.file_id = file_id
        self.user_id = user_id
        self.file_type = file_type
        self.file_size = file_size
        self.uploaded_at = uploaded_at
