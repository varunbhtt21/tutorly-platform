"""Use case for recording a session completion for a student."""

from app.domains.student.entities import StudentProfile
from app.domains.student.repositories import IStudentProfileRepository


class RecordSessionCompletionUseCase:
    """
    Use case for recording a completed session for a student.

    Records that a student has completed a session and updates their
    total session count and total amount spent.
    """

    def __init__(self, student_repo: IStudentProfileRepository):
        """
        Initialize RecordSessionCompletionUseCase.

        Args:
            student_repo: Repository for student profile persistence
        """
        self.student_repo = student_repo

    def execute(self, student_id: int, amount_spent: float) -> StudentProfile:
        """
        Execute the use case to record session completion.

        Args:
            student_id: ID of the student profile
            amount_spent: Amount spent for this session

        Returns:
            Updated StudentProfile with session and spending information

        Raises:
            ValueError: If student profile not found or amount is invalid
            RepositoryError: If database operation fails
        """
        # Retrieve the student profile from repository
        profile = self.student_repo.get_by_id(student_id)

        if not profile:
            raise ValueError(f"Student profile with ID {student_id} not found")

        # Validate amount
        if amount_spent < 0:
            raise ValueError("Amount spent cannot be negative")

        # Record session completion using domain method
        profile.record_session_completion(amount_spent)

        # Save updated profile
        updated_profile = self.student_repo.update(profile)

        return updated_profile
