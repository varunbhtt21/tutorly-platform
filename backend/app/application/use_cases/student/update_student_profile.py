"""Use case for updating a student profile."""

from typing import Optional

from app.domains.student.entities import StudentProfile
from app.domains.student.repositories import IStudentProfileRepository


class UpdateStudentProfileUseCase:
    """
    Use case for updating a student profile.

    Allows students to update their profile information such as
    profile photo, learning goals, and preferred language.
    """

    def __init__(self, student_repo: IStudentProfileRepository):
        """
        Initialize UpdateStudentProfileUseCase.

        Args:
            student_repo: Repository for student profile persistence
        """
        self.student_repo = student_repo

    def execute(
        self,
        student_id: int,
        profile_photo_url: Optional[str] = None,
        learning_goals: Optional[str] = None,
        preferred_language: Optional[str] = None,
        preferred_session_duration: Optional[int] = None,
    ) -> StudentProfile:
        """
        Execute the use case to update student profile.

        Args:
            student_id: ID of the student profile to update
            profile_photo_url: Optional URL to new profile photo
            learning_goals: Optional updated learning goals
            preferred_language: Optional preferred language for tutoring
            preferred_session_duration: Optional preferred session duration in minutes

        Returns:
            Updated StudentProfile

        Raises:
            ValueError: If student profile not found or validation fails
            RepositoryError: If database operation fails
        """
        # Retrieve the student profile from repository
        profile = self.student_repo.get_by_id(student_id)

        if not profile:
            raise ValueError(f"Student profile with ID {student_id} not found")

        # Update profile information
        profile.update_profile(
            profile_photo_url=profile_photo_url,
            learning_goals=learning_goals,
            preferred_language=preferred_language,
            preferred_session_duration=preferred_session_duration,
        )

        # Save updated profile
        updated_profile = self.student_repo.update(profile)

        return updated_profile
