"""Use case for creating a student profile."""

from app.domains.student.entities import StudentProfile
from app.domains.student.repositories import IStudentProfileRepository


class CreateStudentProfileUseCase:
    """
    Use case for creating a new student profile.

    Creates a student profile for a user who is registering as a student.
    Initializes the profile with default preferences and empty statistics.
    """

    def __init__(self, student_repo: IStudentProfileRepository):
        """
        Initialize CreateStudentProfileUseCase.

        Args:
            student_repo: Repository for student profile persistence
        """
        self.student_repo = student_repo

    def execute(self, user_id: int) -> StudentProfile:
        """
        Execute the use case to create student profile.

        Args:
            user_id: User ID who is becoming a student

        Returns:
            Created StudentProfile with ID populated

        Raises:
            ValueError: If user already has a student profile
            RepositoryError: If database operation fails
        """
        # Check if profile already exists
        existing_profile = self.student_repo.get_by_user_id(user_id)
        if existing_profile:
            raise ValueError(f"Student profile already exists for user {user_id}")

        # Create new profile using factory method
        profile = StudentProfile.create_for_user(user_id)

        # Save to repository
        saved_profile = self.student_repo.save(profile)

        return saved_profile
