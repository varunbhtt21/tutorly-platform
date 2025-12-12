from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileDeleted:
    """Domain event fired when a file is deleted."""

    file_id: str
    user_id: str
    deleted_at: datetime

    def __init__(
        self,
        file_id: str,
        user_id: str,
        deleted_at: datetime,
    ) -> None:
        self.file_id = file_id
        self.user_id = user_id
        self.deleted_at = deleted_at
