"""User domain entity with business logic."""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from ..value_objects import Email, Password, UserRole, UserStatus
from ..events import (
    UserRegistered,
    EmailVerified,
    PasswordChanged,
    UserStatusChanged,
    UserProfileUpdated,
)


@dataclass
class User:
    """
    User aggregate root.

    Rich domain entity with business logic and invariants.
    Enforces domain rules and emits domain events.
    """

    # Identity
    id: Optional[int] = None

    # Value Objects
    email: Email = field(default=None)
    password: Password = field(default=None)
    role: UserRole = field(default=UserRole.STUDENT)
    status: UserStatus = field(default=UserStatus.INACTIVE)

    # Attributes
    first_name: str = field(default="")
    last_name: str = field(default="")
    phone_number: Optional[str] = None

    # Flags
    email_verified: bool = False
    terms_accepted: bool = False

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None

    # Domain Events (not persisted)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Initialize domain invariants."""
        # Validate required fields
        if not self.email:
            raise ValueError("Email is required")
        if not self.password:
            raise ValueError("Password is required")

    # ========================================================================
    # Factory Methods (Creation)
    # ========================================================================

    @classmethod
    def register(
        cls,
        email: Email,
        password: Password,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.STUDENT,
        phone_number: Optional[str] = None,
    ) -> "User":
        """
        Register a new user.

        Domain factory method that creates a new user and emits UserRegistered event.

        Args:
            email: User email
            password: User password (already hashed)
            first_name: User first name
            last_name: User last name
            role: User role (default: STUDENT)
            phone_number: Optional phone number

        Returns:
            New User instance

        Raises:
            ValueError: If validation fails
        """
        # Validate
        if not first_name or not first_name.strip():
            raise ValueError("First name is required")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required")

        # Create user
        user = cls(
            email=email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role,
            status=UserStatus.INACTIVE,  # Start inactive until email verified
            email_verified=False,
            terms_accepted=True,  # Assumed accepted during registration
            phone_number=phone_number,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Emit domain event
        user._add_domain_event(
            UserRegistered(
                user_id=user.id,
                email=str(user.email),
                role=user.role,
                registered_at=user.created_at,
            )
        )

        return user

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def verify_email(self) -> None:
        """
        Verify user's email address.

        Domain business logic for email verification.
        Activates account and emits EmailVerified event.
        """
        if self.email_verified:
            raise ValueError("Email already verified")

        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
        self.status = UserStatus.ACTIVE  # Activate account
        self.updated_at = datetime.utcnow()

        # Emit domain event
        self._add_domain_event(
            EmailVerified(
                user_id=self.id,
                email=str(self.email),
                verified_at=self.email_verified_at,
            )
        )

    def change_password(self, new_password: Password) -> None:
        """
        Change user's password.

        Args:
            new_password: New password (already hashed and validated)

        Raises:
            ValueError: If new password is same as old
        """
        if self.password == new_password:
            raise ValueError("New password must be different from current password")

        old_password_hash = self.password.hashed_value
        self.password = new_password
        self.updated_at = datetime.utcnow()

        # Emit domain event
        self._add_domain_event(
            PasswordChanged(
                user_id=self.id,
                email=str(self.email),
                changed_at=self.updated_at,
            )
        )

    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> None:
        """
        Update user profile information.

        Args:
            first_name: New first name
            last_name: New last name
            phone_number: New phone number
        """
        changed = False

        if first_name and first_name.strip() and first_name.strip() != self.first_name:
            self.first_name = first_name.strip()
            changed = True

        if last_name and last_name.strip() and last_name.strip() != self.last_name:
            self.last_name = last_name.strip()
            changed = True

        if phone_number is not None and phone_number != self.phone_number:
            self.phone_number = phone_number
            changed = True

        if changed:
            self.updated_at = datetime.utcnow()

            # Emit domain event
            self._add_domain_event(
                UserProfileUpdated(
                    user_id=self.id,
                    email=str(self.email),
                    updated_at=self.updated_at,
                )
            )

    def suspend(self, reason: str) -> None:
        """
        Suspend user account.

        Args:
            reason: Reason for suspension
        """
        if self.status == UserStatus.SUSPENDED:
            raise ValueError("User is already suspended")

        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot suspend deleted user")

        old_status = self.status
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

        # Emit domain event
        self._add_domain_event(
            UserStatusChanged(
                user_id=self.id,
                email=str(self.email),
                old_status=old_status,
                new_status=self.status,
                reason=reason,
                changed_at=self.updated_at,
            )
        )

    def activate(self) -> None:
        """
        Activate user account.

        Can activate from INACTIVE or SUSPENDED status.
        """
        if not self.status.can_be_activated():
            raise ValueError(f"Cannot activate user with status: {self.status}")

        old_status = self.status
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

        # Emit domain event
        self._add_domain_event(
            UserStatusChanged(
                user_id=self.id,
                email=str(self.email),
                old_status=old_status,
                new_status=self.status,
                reason="Account activated",
                changed_at=self.updated_at,
            )
        )

    def ban(self, reason: str) -> None:
        """
        Ban user account permanently.

        Args:
            reason: Reason for ban
        """
        if self.status == UserStatus.BANNED:
            raise ValueError("User is already banned")

        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot ban deleted user")

        old_status = self.status
        self.status = UserStatus.BANNED
        self.updated_at = datetime.utcnow()

        # Emit domain event
        self._add_domain_event(
            UserStatusChanged(
                user_id=self.id,
                email=str(self.email),
                old_status=old_status,
                new_status=self.status,
                reason=reason,
                changed_at=self.updated_at,
            )
        )

    def soft_delete(self) -> None:
        """
        Soft delete user account.

        Marks user as deleted without removing from database.
        """
        if self.status == UserStatus.DELETED:
            raise ValueError("User is already deleted")

        old_status = self.status
        self.status = UserStatus.DELETED
        self.updated_at = datetime.utcnow()

        # Emit domain event
        self._add_domain_event(
            UserStatusChanged(
                user_id=self.id,
                email=str(self.email),
                old_status=old_status,
                new_status=self.status,
                reason="User deleted account",
                changed_at=self.updated_at,
            )
        )

    def record_login(self) -> None:
        """Record user login timestamp."""
        if not self.status.can_login():
            raise ValueError(f"User cannot login with status: {self.status}")

        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    # ========================================================================
    # Domain Properties
    # ========================================================================

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status.is_active

    @property
    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.role.is_student

    @property
    def is_instructor(self) -> bool:
        """Check if user is an instructor."""
        return self.role.is_instructor

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role.is_admin

    @property
    def can_login(self) -> bool:
        """Check if user can login."""
        return self.status.can_login()

    def can_teach(self) -> bool:
        """Check if user can teach."""
        return self.role.can_teach() and self.is_active

    def can_learn(self) -> bool:
        """Check if user can learn."""
        return self.role.can_learn() and self.is_active

    # ========================================================================
    # Domain Events
    # ========================================================================

    def _add_domain_event(self, event) -> None:
        """Add domain event to event list."""
        self._domain_events.append(event)

    def get_domain_events(self) -> List:
        """Get all domain events."""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    # ========================================================================
    # Equality
    # ========================================================================

    def __eq__(self, other) -> bool:
        """User equality based on ID."""
        if not isinstance(other, User):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make User hashable."""
        return hash(self.id) if self.id else hash(id(self))
