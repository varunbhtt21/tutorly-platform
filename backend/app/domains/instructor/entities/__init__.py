"""Instructor domain entities."""

from .instructor_profile import InstructorProfile
from .education import Education
from .experience import Experience
from .instructor_dashboard import InstructorDashboard

__all__ = [
    "InstructorProfile",
    "Education",
    "Experience",
    "InstructorDashboard",
]
