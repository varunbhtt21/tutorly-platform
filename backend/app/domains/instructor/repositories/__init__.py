"""Instructor domain repository interfaces."""

from .instructor_repository import IInstructorProfileRepository
from .education_repository import IEducationRepository
from .experience_repository import IExperienceRepository

__all__ = [
    "IInstructorProfileRepository",
    "IEducationRepository",
    "IExperienceRepository",
]
