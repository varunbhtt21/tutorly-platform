"""
Classroom Router.

API endpoints for video classroom functionality.
Provides session-based video room management using pluggable video providers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.domains.user.entities import User
from app.core.dependencies import (
    get_current_user,
    get_create_classroom_use_case,
    get_join_classroom_use_case,
    get_end_classroom_use_case,
)
from app.application.use_cases.classroom import (
    CreateClassroomUseCase,
    CreateClassroomRequest,
    JoinClassroomUseCase,
    JoinClassroomRequest,
    EndClassroomUseCase,
)
from app.domains.classroom.services.video_provider import (
    VideoProviderError,
    RoomCreationError,
    TokenCreationError,
)


router = APIRouter(prefix="/classroom", tags=["Classroom"])


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateClassroomResponseModel(BaseModel):
    """Response for classroom creation."""
    classroom_id: int
    session_id: int
    room_name: str
    room_url: str
    provider: str
    status: str
    expires_at: Optional[datetime] = None


class JoinClassroomResponseModel(BaseModel):
    """Response with meeting token for joining."""
    room_url: str
    token: str
    room_id: str  # Provider-specific room ID (needed for 100ms SDK)
    room_name: str
    participant_name: str
    participant_role: str
    expires_at: datetime
    provider: str


class EndClassroomResponseModel(BaseModel):
    """Response for ending a classroom."""
    success: bool
    message: str


class ClassroomStatusResponseModel(BaseModel):
    """Response for classroom status check."""
    session_id: int
    room_name: str
    status: str
    is_joinable: bool
    provider: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    started_at: Optional[datetime] = None


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/{session_id}/create",
    response_model=CreateClassroomResponseModel,
    summary="Create a classroom for a session",
    description="Creates a video room for a tutoring session. Idempotent - returns existing room if already created.",
)
async def create_classroom(
    session_id: int,
    current_user: User = Depends(get_current_user),
    use_case: CreateClassroomUseCase = Depends(get_create_classroom_use_case),
):
    """
    Create a video classroom for a tutoring session.

    Only participants (instructor or student) can create the classroom.
    This endpoint is idempotent - calling it multiple times returns the same room.
    """
    try:
        classroom = use_case.execute(
            CreateClassroomRequest(
                session_id=session_id,
                user_id=current_user.id,
            )
        )

        return CreateClassroomResponseModel(
            classroom_id=classroom.id,
            session_id=classroom.session_id,
            room_name=classroom.room_name,
            room_url=classroom.room_url,
            provider=classroom.provider,
            status=classroom.status.value,
            expires_at=classroom.expires_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RoomCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to create video room: {str(e)}",
        )
    except VideoProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video provider error: {str(e)}",
        )


@router.post(
    "/{session_id}/join",
    response_model=JoinClassroomResponseModel,
    summary="Join a classroom",
    description="Get a meeting token to join the classroom video call.",
)
async def join_classroom(
    session_id: int,
    current_user: User = Depends(get_current_user),
    use_case: JoinClassroomUseCase = Depends(get_join_classroom_use_case),
):
    """
    Get a meeting token to join a classroom.

    Returns a URL with authentication token for the video call.
    Only participants can join.
    """
    try:
        result = use_case.execute(
            JoinClassroomRequest(
                session_id=session_id,
                user_id=current_user.id,
            )
        )

        return JoinClassroomResponseModel(
            room_url=result.room_url,
            token=result.token,
            room_id=result.room_id,
            room_name=result.room_name,
            participant_name=result.participant_name,
            participant_role=result.participant_role,
            expires_at=result.expires_at,
            provider=result.provider,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except TokenCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to create meeting token: {str(e)}",
        )
    except VideoProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video provider error: {str(e)}",
        )


@router.post(
    "/{session_id}/end",
    response_model=EndClassroomResponseModel,
    summary="End a classroom session",
    description="End the video call and mark the session as completed. Only instructors can end sessions.",
)
async def end_classroom(
    session_id: int,
    current_user: User = Depends(get_current_user),
    use_case: EndClassroomUseCase = Depends(get_end_classroom_use_case),
):
    """
    End a classroom session.

    Only the instructor can end the session.
    This marks the classroom as ended and cleans up resources.
    """
    try:
        use_case.execute(
            session_id=session_id,
            user_id=current_user.id,
        )

        return EndClassroomResponseModel(
            success=True,
            message="Classroom ended successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except VideoProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video provider error: {str(e)}",
        )


@router.get(
    "/{session_id}/status",
    response_model=ClassroomStatusResponseModel,
    summary="Get classroom status",
    description="Check the current status of a classroom.",
)
async def get_classroom_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    use_case: JoinClassroomUseCase = Depends(get_join_classroom_use_case),
):
    """
    Get the status of a classroom.

    Returns room status and whether it's joinable.
    """
    # Reuse join use case's repository access
    classroom = use_case.classroom_repo.get_by_session_id(session_id)

    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom not found for session {session_id}",
        )

    # Verify user is participant
    if not classroom.can_join(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this classroom",
        )

    return ClassroomStatusResponseModel(
        session_id=classroom.session_id,
        room_name=classroom.room_name,
        status=classroom.status.value,
        is_joinable=classroom.is_joinable,
        provider=classroom.provider,
        created_at=classroom.created_at,
        expires_at=classroom.expires_at,
        started_at=classroom.started_at,
    )
