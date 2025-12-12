"""Login user use case."""

from typing import Callable
from app.domains.user.entities import User
from app.domains.user.repositories import IUserRepository
from app.domains.user.value_objects import Email


class LoginUserUseCase:
    """
    Login user use case.

    Orchestrates the login process by:
    1. Loading user by email
    2. Verifying password
    3. Recording login timestamp
    4. Persisting updated user

    This use case bridges the application layer and domain layer,
    ensuring authentication and login recording are properly handled.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize LoginUserUseCase.

        Args:
            user_repo: User repository for persistence
        """
        self.user_repo = user_repo

    def execute(
        self,
        email: str,
        password: str,
        password_verifier: Callable[[str, str], bool],
    ) -> User:
        """
        Execute user login.

        This method:
        1. Creates Email value object and retrieves user by email
        2. Verifies password using password verifier function
        3. Calls user.record_login() to update last login timestamp
        4. Saves updated user to repository
        5. Returns logged-in user

        Args:
            email: User email address
            password: Plain text password to verify
            password_verifier: Function to verify password against hash
                             Takes (plain_password, hashed_password) -> bool

        Returns:
            Logged-in User entity

        Raises:
            ValueError: If user not found, password incorrect, or user cannot login
        """
        # Create Email value object
        email_vo = Email(value=email)

        # Get user from repository
        user = self.user_repo.get_by_email(email_vo)
        if user is None:
            raise ValueError(f"User with email '{email}' not found")

        # Verify password
        if not user.password.verify(password, password_verifier):
            raise ValueError("Invalid password")

        # Record login - validates user can login and updates last_login_at
        # This method enforces business rules (e.g., user must be ACTIVE)
        user.record_login()

        # Persist updated user with new last_login_at timestamp
        logged_in_user = self.user_repo.save(user)

        return logged_in_user
