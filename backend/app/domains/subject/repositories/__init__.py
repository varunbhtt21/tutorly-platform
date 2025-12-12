"""Subject domain repositories."""

from .subject_repository import ISubjectRepository
from .instructor_subject_repository import IInstructorSubjectRepository

__all__ = [
    "ISubjectRepository",
    "IInstructorSubjectRepository",
]
