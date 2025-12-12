"""
Custom exception classes for domain-specific errors.
Follows Domain-Driven Design principles for clear error handling.
"""

from typing import Any, Dict, Optional


class TutorlyException(Exception):
    """Base exception for all Tutorly platform errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================


class AuthenticationException(TutorlyException):
    """Base exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class InvalidCredentialsError(AuthenticationException):
    """Raised when login credentials are invalid."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, error_code="INVALID_CREDENTIALS")


class AccountLockedError(AuthenticationException):
    """Raised when account is locked due to failed login attempts."""

    def __init__(self, locked_until: str):
        super().__init__(
            f"Account locked until {locked_until}",
            error_code="ACCOUNT_LOCKED",
            details={"locked_until": locked_until},
        )


class EmailNotVerifiedError(AuthenticationException):
    """Raised when user tries to login without email verification."""

    def __init__(self, message: str = "Email not verified. Please verify your email."):
        super().__init__(message, error_code="EMAIL_NOT_VERIFIED")


class InvalidTokenError(AuthenticationException):
    """Raised when JWT token is invalid or expired."""

    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, error_code="INVALID_TOKEN")


class AuthorizationException(TutorlyException):
    """Base exception for authorization errors."""

    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class InsufficientPermissionsError(AuthorizationException):
    """Raised when user lacks required permissions."""

    def __init__(self, required_role: str):
        super().__init__(
            f"Insufficient permissions. Required role: {required_role}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_role": required_role},
        )


# ============================================================================
# User & Profile Exceptions
# ============================================================================


class UserException(TutorlyException):
    """Base exception for user-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class UserAlreadyExistsError(UserException):
    """Raised when attempting to create a user with existing email."""

    def __init__(self, email: str):
        super().__init__(
            f"User with email '{email}' already exists",
            error_code="USER_ALREADY_EXISTS",
            details={"email": email},
        )


class UserNotFoundError(UserException):
    """Raised when user cannot be found."""

    def __init__(self, identifier: str, identifier_type: str = "id"):
        super().__init__(
            f"User not found with {identifier_type}: {identifier}",
            status_code=404,
            error_code="USER_NOT_FOUND",
            details={"identifier": identifier, "identifier_type": identifier_type},
        )


class AccountSuspendedError(UserException):
    """Raised when user account is suspended."""

    def __init__(self, reason: Optional[str] = None):
        message = "Account suspended"
        if reason:
            message += f": {reason}"
        super().__init__(message, status_code=403, error_code="ACCOUNT_SUSPENDED")


class AccountBannedError(UserException):
    """Raised when user account is banned."""

    def __init__(self, reason: Optional[str] = None):
        message = "Account permanently banned"
        if reason:
            message += f": {reason}"
        super().__init__(message, status_code=403, error_code="ACCOUNT_BANNED")


# ============================================================================
# Instructor Exceptions
# ============================================================================


class InstructorException(TutorlyException):
    """Base exception for instructor-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class InstructorNotVerifiedError(InstructorException):
    """Raised when instructor tries to perform action requiring verification."""

    def __init__(self):
        super().__init__(
            "Instructor profile not verified. Please complete verification first.",
            error_code="INSTRUCTOR_NOT_VERIFIED",
        )


class OnboardingIncompleteError(InstructorException):
    """Raised when instructor tries to submit incomplete onboarding."""

    def __init__(self, missing_steps: list):
        super().__init__(
            f"Onboarding incomplete. Missing steps: {', '.join(map(str, missing_steps))}",
            error_code="ONBOARDING_INCOMPLETE",
            details={"missing_steps": missing_steps},
        )


class ProfileAlreadyExistsError(InstructorException):
    """Raised when trying to create duplicate profile."""

    def __init__(self, profile_type: str):
        super().__init__(
            f"{profile_type} profile already exists",
            error_code="PROFILE_ALREADY_EXISTS",
            details={"profile_type": profile_type},
        )


class InstructorNotFoundException(InstructorException):
    """Raised when instructor profile cannot be found."""

    def __init__(self, message: str = "Instructor profile not found"):
        super().__init__(
            message,
            status_code=404,
            error_code="INSTRUCTOR_NOT_FOUND",
        )


class InvalidOnboardingStepError(InstructorException):
    """Raised when trying to access an invalid onboarding step."""

    def __init__(self, message: str = "Invalid onboarding step"):
        super().__init__(
            message,
            error_code="INVALID_ONBOARDING_STEP",
        )


class ProfileIncompleteError(InstructorException):
    """Raised when trying to perform action with incomplete profile."""

    def __init__(self, message: str = "Profile incomplete"):
        super().__init__(
            message,
            error_code="PROFILE_INCOMPLETE",
        )


# ============================================================================
# Validation Exceptions
# ============================================================================


class ValidationException(TutorlyException):
    """Base exception for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        super().__init__(message, status_code=422, details=details, **kwargs)


class InvalidEmailError(ValidationException):
    """Raised when email format is invalid."""

    def __init__(self, email: str):
        super().__init__(
            f"Invalid email format: {email}",
            field="email",
            error_code="INVALID_EMAIL",
        )


class WeakPasswordError(ValidationException):
    """Raised when password doesn't meet requirements."""

    def __init__(self, requirements: list):
        super().__init__(
            f"Password doesn't meet requirements: {', '.join(requirements)}",
            field="password",
            error_code="WEAK_PASSWORD",
            details={"requirements": requirements},
        )


class InvalidPhoneNumberError(ValidationException):
    """Raised when phone number format is invalid."""

    def __init__(self, phone: str):
        super().__init__(
            f"Invalid phone number: {phone}",
            field="phone_number",
            error_code="INVALID_PHONE",
        )


# ============================================================================
# Business Logic Exceptions
# ============================================================================


class BookingException(TutorlyException):
    """Base exception for booking-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class SlotNotAvailableError(BookingException):
    """Raised when trying to book unavailable time slot."""

    def __init__(self, slot_time: str):
        super().__init__(
            f"Time slot not available: {slot_time}",
            error_code="SLOT_NOT_AVAILABLE",
            details={"slot_time": slot_time},
        )


class SessionException(TutorlyException):
    """Base exception for session-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class SessionNotFoundError(SessionException):
    """Raised when session cannot be found."""

    def __init__(self, session_id: int):
        super().__init__(
            f"Session not found: {session_id}",
            status_code=404,
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id},
        )


class PaymentException(TutorlyException):
    """Base exception for payment-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class PaymentFailedError(PaymentException):
    """Raised when payment processing fails."""

    def __init__(self, reason: str):
        super().__init__(
            f"Payment failed: {reason}",
            error_code="PAYMENT_FAILED",
            details={"reason": reason},
        )


class InsufficientFundsError(PaymentException):
    """Raised when wallet has insufficient funds."""

    def __init__(self, required: float, available: float):
        super().__init__(
            f"Insufficient funds. Required: ${required}, Available: ${available}",
            error_code="INSUFFICIENT_FUNDS",
            details={"required": required, "available": available},
        )


# ============================================================================
# Messaging Exceptions
# ============================================================================


class MessagingException(TutorlyException):
    """Base exception for messaging-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class MessageViolationError(MessagingException):
    """Raised when message contains prohibited content."""

    def __init__(self, violation_type: str, content_snippet: str):
        super().__init__(
            f"Message contains prohibited content: {violation_type}",
            error_code="MESSAGE_VIOLATION",
            details={
                "violation_type": violation_type,
                "content_snippet": content_snippet[:50],  # First 50 chars
            },
        )


class ConversationNotFoundException(MessagingException):
    """Raised when conversation cannot be found."""

    def __init__(self, conversation_id: int):
        super().__init__(
            f"Conversation not found: {conversation_id}",
            status_code=404,
            error_code="CONVERSATION_NOT_FOUND",
        )


# ============================================================================
# File Upload Exceptions
# ============================================================================


class FileUploadException(TutorlyException):
    """Base exception for file upload errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class FileTooLargeError(FileUploadException):
    """Raised when uploaded file exceeds size limit."""

    def __init__(self, file_size: int, max_size: int, file_type: str):
        super().__init__(
            f"{file_type} file too large: {file_size}MB (max: {max_size}MB)",
            error_code="FILE_TOO_LARGE",
            details={"file_size": file_size, "max_size": max_size, "file_type": file_type},
        )


class InvalidFileTypeError(FileUploadException):
    """Raised when file type is not allowed."""

    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            f"Invalid file type: {file_type}. Allowed: {', '.join(allowed_types)}",
            error_code="INVALID_FILE_TYPE",
            details={"file_type": file_type, "allowed_types": allowed_types},
        )


class FileUploadError(FileUploadException):
    """General file upload error."""

    def __init__(self, message: str):
        super().__init__(message, error_code="FILE_UPLOAD_ERROR")


# ============================================================================
# Database Exceptions
# ============================================================================


class DatabaseException(TutorlyException):
    """Base exception for database errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class RecordNotFoundError(DatabaseException):
    """Raised when database record cannot be found."""

    def __init__(self, model_name: str, identifier: Any):
        super().__init__(
            f"{model_name} not found: {identifier}",
            status_code=404,
            error_code="RECORD_NOT_FOUND",
            details={"model": model_name, "identifier": str(identifier)},
        )


class DatabaseConstraintError(DatabaseException):
    """Raised when database constraint is violated."""

    def __init__(self, constraint: str):
        super().__init__(
            f"Database constraint violated: {constraint}",
            error_code="CONSTRAINT_VIOLATION",
            details={"constraint": constraint},
        )
