"""Register user use case."""

from typing import Optional, Callable
from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository
from app.domains.user.value_objects import Email, Password, UserRole
from app.domains.instructor.entities import InstructorProfile
from app.domains.instructor.repositories import IInstructorProfileRepository


class RegisterUserUseCase:
    """
    Register new user use case.

    Orchestrates the registration process by:
    1. Validating email uniqueness
    2. Creating password value object with hashing
    3. Creating User aggregate root via factory method
    4. Persisting to repository
    5. Creating instructor profile if registering as instructor

    This use case bridges the application layer and domain layer,
    ensuring business rules are enforced.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        instructor_repo: Optional[IInstructorProfileRepository] = None,
    ):
        """
        Initialize RegisterUserUseCase.

        Args:
            user_repo: User repository for persistence
            instructor_repo: Optional instructor repository for creating instructor profiles
        """
        self.user_repo = user_repo
        self.instructor_repo = instructor_repo

    def execute(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        phone_number: Optional[str] = None,
        password_hasher: Optional[Callable[[str], str]] = None,
    ) -> User:
        """
        Execute user registration.

        This method:
        1. Creates Email value object (validates email format)
        2. Checks if email already exists
        3. Creates Password value object with hashing
        4. Calls User.register() factory method
        5. Saves user to repository
        6. Returns persisted user

        Args:
            email: User email address
            password: Plain text password (will be hashed)
            first_name: User first name
            last_name: User last name
            role: User role (STUDENT, INSTRUCTOR, ADMIN)
            phone_number: Optional phone number
            password_hasher: Function to hash password (dependency injection)

        Returns:
            Registered User entity with ID

        Raises:
            ValueError: If email already exists, email is invalid, or password is weak
        """
        # Validate and create Email value object
        email_vo = Email(value=email)

        # Check if email already exists
        if self.user_repo.email_exists(email_vo):
            raise ValueError(f"Email '{email}' is already registered")

        # Use default hasher if not provided (for testing/specific scenarios)
        if password_hasher is None:
            # Import here to avoid circular imports
            from app.core.security import get_password_hash
            password_hasher = get_password_hash

        # Create Password value object (validates strength and hashes)
        password_vo = Password.create_from_plain(password, password_hasher)

        # Create User aggregate root via factory method
        # Factory method handles validation and emits domain events
        user = User.register(
            email=email_vo,
            password=password_vo,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone_number=phone_number,
        )

        # Persist to repository
        # Repository returns user with assigned ID
        saved_user = self.user_repo.save(user)

        # If registering as instructor, create instructor profile
        if role == UserRole.INSTRUCTOR and self.instructor_repo is not None:
            instructor_profile = InstructorProfile.create_for_user(saved_user.id)
            self.instructor_repo.save(instructor_profile)

        return saved_user
