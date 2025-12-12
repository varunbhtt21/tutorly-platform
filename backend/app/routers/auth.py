"""
Authentication API Router - Pure DDD Implementation.

Handles all authentication-related HTTP endpoints using Pure DDD principles:
- Thin controllers: Only handle HTTP concerns
- Delegate business logic to use cases
- Use domain entities and value objects
- Proper error handling and HTTP status codes
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    create_password_reset_token,
    verify_password_reset_token,
    get_password_hash,
)
from app.core.dependencies import (
    get_register_user_use_case,
    get_login_user_use_case,
    get_verify_email_use_case,
    get_update_user_profile_use_case,
    get_current_active_user,
    get_password_hasher,
    get_password_verifier,
    get_user_repository,
)
from app.domains.user.entities import User
from app.domains.user.value_objects import UserRole, Email
from app.domains.user.repositories import IUserRepository
from app.application.use_cases.user import (
    RegisterUserUseCase,
    LoginUserUseCase,
    VerifyEmailUseCase,
    UpdateUserProfileUseCase,
)


# ============================================================================
# Request/Response DTOs (Inline Pydantic Models)
# ============================================================================


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: UserRole
    phone_number: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str
    remember_me: bool = False  # If True, use longer refresh token expiry


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class EmailVerificationRequest(BaseModel):
    """Email verification request."""
    token: str


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """User response DTO."""
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    phone_number: Optional[str] = None
    email_verified: bool
    is_active: bool

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        """Create response from domain entity."""
        return cls(
            id=user.id,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            phone_number=user.phone_number,
            email_verified=user.email_verified,
            is_active=user.is_active,
        )


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthUserResponse(BaseModel):
    """Authenticated user response with tokens."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Create router
router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def create_tokens_for_user(user: User, remember_me: bool = False) -> dict:
    """
    Create access and refresh tokens for a user.

    Args:
        user: Domain User entity
        remember_me: If True, create refresh token with longer expiry

    Returns:
        dict: Dictionary with access_token, refresh_token, expires_in
    """
    token_data = {
        "sub": str(user.id),
        "email": user.email.value,
        "role": user.role.value,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data, remember_me=remember_me)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def handle_domain_exception(e: Exception) -> None:
    """
    Convert domain exceptions to HTTP exceptions.

    Args:
        e: Exception from domain or use case layer

    Raises:
        HTTPException: Appropriate HTTP exception
    """
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    logger.error(f"Domain exception: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    error_message = str(e)

    # Map common domain errors to HTTP status codes
    if "already registered" in error_message.lower() or "already exists" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "USER_ALREADY_EXISTS", "message": error_message},
        )
    elif "not found" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "USER_NOT_FOUND", "message": error_message},
        )
    elif "invalid password" in error_message.lower() or "invalid credentials" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )
    elif "cannot login" in error_message.lower() or "not active" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "ACCOUNT_INACTIVE", "message": error_message},
        )
    elif "already verified" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMAIL_ALREADY_VERIFIED", "message": error_message},
        )
    elif "invalid email" in error_message.lower() or "password" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "VALIDATION_ERROR", "message": error_message},
        )
    else:
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
        )


# ============================================================================
# Authentication Endpoints
# ============================================================================


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account (instructor or student) with email verification",
)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
    password_hasher=Depends(get_password_hasher),
):
    """
    Register a new user.

    - **email**: Valid email address (unique)
    - **password**: Strong password (min 8 chars)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **role**: User role (instructor or student)
    - **phone_number**: Optional phone number

    Returns user data with access and refresh tokens.
    """
    try:
        # Execute use case
        user = use_case.execute(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            role=request.role,
            phone_number=request.phone_number,
            password_hasher=password_hasher,
        )

        # Create tokens
        tokens = create_tokens_for_user(user)

        return AuthUserResponse(
            user=UserResponse.from_domain(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/login",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password",
)
async def login(
    request: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
    password_verifier=Depends(get_password_verifier),
):
    """
    Login user with email and password.

    - **email**: User's email address
    - **password**: User's password
    - **remember_me**: If true, extend refresh token expiry to 30 days

    Returns user data with access and refresh tokens.

    Raises:
    - **401 Unauthorized**: Invalid credentials
    - **403 Forbidden**: Account locked, suspended, or banned
    """
    try:
        # Execute use case
        user = use_case.execute(
            email=request.email,
            password=request.password,
            password_verifier=password_verifier,
        )

        # Create tokens (with longer expiry if remember_me is True)
        tokens = create_tokens_for_user(user, remember_me=request.remember_me)

        return AuthUserResponse(
            user=UserResponse.from_domain(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Generate new access token using refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Refresh access token.

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens.

    Raises:
    - **401 Unauthorized**: Invalid or expired refresh token
    """
    try:
        # Decode refresh token
        payload = decode_token(request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Invalid or expired refresh token"},
            )

        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Invalid token payload"},
            )

        user = user_repo.get_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "USER_NOT_FOUND", "message": "User not found"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error_code": "ACCOUNT_INACTIVE", "message": f"Account {user.status.value}"},
            )

        # Create new tokens
        tokens = create_tokens_for_user(user)

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Failed to refresh token"},
        )


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email to user",
)
async def request_password_reset(
    request: PasswordResetRequest,
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Request password reset.

    - **email**: User's email address

    Sends password reset email with token.
    Returns success message regardless of whether email exists (security).
    """
    try:
        # Always return success to prevent email enumeration
        # In production, this would send an email if the user exists
        try:
            email_vo = Email(value=request.email)
            user = user_repo.get_by_email(email_vo)
            if user:
                reset_token = create_password_reset_token(request.email)
                # TODO: Send reset email via email service
                # email_service.send_password_reset_email(request.email, reset_token)
        except Exception:
            # Silently fail to prevent email enumeration
            pass

        return MessageResponse(
            message="If the email exists, a password reset link has been sent."
        )

    except Exception as e:
        # Even on error, return success message for security
        return MessageResponse(
            message="If the email exists, a password reset link has been sent."
        )


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm password reset",
    description="Reset password using token from email",
)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    user_repo: IUserRepository = Depends(get_user_repository),
):
    """
    Confirm password reset with token.

    - **token**: Password reset token from email
    - **new_password**: New password

    Returns success message.

    Raises:
    - **401 Unauthorized**: Invalid or expired token
    """
    try:
        # Verify token
        email = verify_password_reset_token(request.token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Invalid or expired reset token"},
            )

        # Get user
        email_vo = Email(value=email)
        user = user_repo.get_by_email(email_vo)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": "USER_NOT_FOUND", "message": "User not found"},
            )

        # Change password using domain method
        from app.domains.user.value_objects import Password
        new_password = Password.create_from_plain(request.new_password, get_password_hash)
        user.change_password(new_password)

        # Save updated user
        user_repo.save(user)

        return MessageResponse(message="Password reset successfully")

    except HTTPException:
        raise
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Failed to reset password"},
        )


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email",
    description="Verify user's email address using token",
)
async def verify_email(
    request: EmailVerificationRequest,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_use_case),
):
    """
    Verify email address.

    - **token**: Email verification token

    Returns success message.

    Raises:
    - **401 Unauthorized**: Invalid or expired token
    """
    try:
        # Decode token to get user_id
        payload = decode_token(request.token)
        if not payload or payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Invalid or expired verification token"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Invalid token payload"},
            )

        # Execute use case
        use_case.execute(user_id=int(user_id))

        return MessageResponse(message="Email verified successfully")

    except HTTPException:
        raise
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Failed to verify email"},
        )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change password for authenticated user",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    user_repo: IUserRepository = Depends(get_user_repository),
    password_verifier=Depends(get_password_verifier),
):
    """
    Change password for authenticated user.

    - **current_password**: Current password (for verification)
    - **new_password**: New password

    Requires authentication.

    Returns success message.

    Raises:
    - **401 Unauthorized**: Current password is incorrect
    """
    try:
        # Verify current password
        if not current_user.password.verify(request.current_password, password_verifier):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_CREDENTIALS", "message": "Current password is incorrect"},
            )

        # Create new password value object
        from app.domains.user.value_objects import Password
        new_password = Password.create_from_plain(request.new_password, get_password_hash)

        # Change password using domain method
        current_user.change_password(new_password)

        # Save updated user
        user_repo.save(current_user)

        return MessageResponse(message="Password changed successfully")

    except HTTPException:
        raise
    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Failed to change password"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get authenticated user's profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user's profile.

    Requires authentication.

    Returns user profile data.
    """
    return UserResponse.from_domain(current_user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout current user (client should discard tokens)",
)
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """
    Logout user.

    Note: Since we're using stateless JWT tokens, the client is responsible
    for discarding the tokens. This endpoint exists for consistency and
    future token blacklisting if needed.

    Returns success message.
    """
    # TODO: Implement token blacklisting with Redis if needed
    # For now, just return success (client handles token removal)

    return MessageResponse(
        message=f"User {current_user.email.value} logged out successfully"
    )
