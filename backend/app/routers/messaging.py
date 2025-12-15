"""
Messaging REST API Router.

Provides REST endpoints for messaging functionality.
Uses DDD use cases for business logic.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user_allow_inactive
from app.domains.user.entities import User as CurrentUser
from app.database.models import (
    User as UserModel,
    Session as SessionModel,
    InstructorProfile,
)

# Domain imports
from app.domains.messaging.value_objects import MessageType, MessageStatus
from app.domains.messaging.entities import Conversation, Message

# Use case imports
from app.application.use_cases.messaging import (
    StartConversationUseCase,
    SendMessageUseCase,
    GetConversationsUseCase,
    GetMessagesUseCase,
    MarkMessagesReadUseCase,
    CheckFeatureAccessUseCase,
    FeatureAccess,
    GetUnreadCountUseCase,
)

# Repository imports
from app.infrastructure.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyMessageRepository,
    SQLAlchemyReadStatusRepository,
)


router = APIRouter(prefix="/messaging", tags=["messaging"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class UserBasicResponse(BaseModel):
    """Basic user info for messaging."""
    id: int
    first_name: str
    last_name: str
    profile_photo_url: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    id: int
    participant_1_id: int
    participant_2_id: int
    other_participant: Optional[UserBasicResponse] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Message response schema."""
    id: int
    conversation_id: int
    sender: UserBasicResponse
    content: str
    message_type: str
    status: str
    reply_to_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StartConversationRequest(BaseModel):
    """Request to start a conversation."""
    recipient_id: int = Field(..., description="User ID to start conversation with")


class SendMessageRequest(BaseModel):
    """Request to send a message."""
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: str = Field(default="text", description="text, image, or file")
    reply_to_id: Optional[int] = None


class MarkReadRequest(BaseModel):
    """Request to mark messages as read."""
    message_id: int = Field(..., description="Mark all messages up to this ID as read")


class FeatureAccessResponse(BaseModel):
    """Feature access response schema."""
    can_send_text: bool
    can_send_image: bool
    can_send_file: bool
    has_booking: bool


class UnreadCountResponse(BaseModel):
    """Unread count response schema."""
    unread_count: int


# ============================================================================
# Session Repository Adapter for Feature Access
# ============================================================================

class SessionRepositoryAdapter:
    """Adapter for checking if booking exists between users."""

    def __init__(self, db: Session):
        self.db = db

    def has_booked_session_between(self, user_1_id: int, user_2_id: int) -> bool:
        """Check if any session exists between two users."""
        session = self.db.query(SessionModel).filter(
            ((SessionModel.student_id == user_1_id) & (SessionModel.instructor_id == user_2_id)) |
            ((SessionModel.student_id == user_2_id) & (SessionModel.instructor_id == user_1_id))
        ).first()
        return session is not None


# ============================================================================
# Helper Functions
# ============================================================================

def get_user_basic_info(db: Session, user_id: int) -> Optional[UserBasicResponse]:
    """Get basic user info."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None

    # Get profile photo
    profile_photo = None
    if user.role.value == "instructor":
        instructor_profile = db.query(InstructorProfile).filter(
            InstructorProfile.user_id == user_id
        ).first()
        if instructor_profile:
            profile_photo = instructor_profile.profile_photo_url

    return UserBasicResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        profile_photo_url=profile_photo,
        role=user.role.value,
    )


def conversation_to_response(
    conversation: Conversation,
    db: Session,
    current_user_id: int,
    unread_count: int = 0,
) -> ConversationResponse:
    """Convert domain Conversation to response."""
    other_id = conversation.get_other_participant_id(current_user_id)
    other_participant = get_user_basic_info(db, other_id)

    return ConversationResponse(
        id=conversation.id,
        participant_1_id=conversation.participant_1_id,
        participant_2_id=conversation.participant_2_id,
        other_participant=other_participant,
        last_message_at=conversation.last_message_at,
        unread_count=unread_count,
        created_at=conversation.created_at,
    )


def message_to_response(message: Message, db: Session) -> MessageResponse:
    """Convert domain Message to response."""
    sender = get_user_basic_info(db, message.sender_id)

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender=sender,
        content=message.content,
        message_type=message.message_type.value,
        status=message.status.value,
        reply_to_id=message.reply_to_id,
        created_at=message.created_at,
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Get all conversations for current user."""
    # Create repositories
    conversation_repo = SQLAlchemyConversationRepository(db)
    message_repo = SQLAlchemyMessageRepository(db)
    read_status_repo = SQLAlchemyReadStatusRepository(db)

    # Execute use case
    use_case = GetConversationsUseCase(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        read_status_repo=read_status_repo,
    )

    results = use_case.execute(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    # Convert to responses
    return [
        conversation_to_response(
            conversation=r["conversation"],
            db=db,
            current_user_id=current_user.id,
            unread_count=r["unread_count"],
        )
        for r in results
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Get a specific conversation."""
    conversation_repo = SQLAlchemyConversationRepository(db)
    message_repo = SQLAlchemyMessageRepository(db)
    read_status_repo = SQLAlchemyReadStatusRepository(db)

    conversation = conversation_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if not conversation.is_participant(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Get read status for unread count
    read_statuses = read_status_repo.get_user_read_statuses(current_user.id)
    read_status = read_statuses.get(conversation_id)
    last_read_id = read_status.last_read_message_id if read_status else None

    unread_count = message_repo.count_unread_for_user(
        conversation_id=conversation_id,
        user_id=current_user.id,
        last_read_message_id=last_read_id,
    )

    return conversation_to_response(
        conversation=conversation,
        db=db,
        current_user_id=current_user.id,
        unread_count=unread_count,
    )


@router.post("/conversations", response_model=ConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Start a new conversation or get existing one."""
    # Validate recipient exists
    recipient = db.query(UserModel).filter(UserModel.id == request.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found",
        )

    # Create repository and execute use case
    conversation_repo = SQLAlchemyConversationRepository(db)

    use_case = StartConversationUseCase(conversation_repo=conversation_repo)

    try:
        conversation = use_case.execute(
            initiator_id=current_user.id,
            recipient_id=request.recipient_id,
        )
        db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return conversation_to_response(
        conversation=conversation,
        db=db,
        current_user_id=current_user.id,
        unread_count=0,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Get messages for a conversation."""
    conversation_repo = SQLAlchemyConversationRepository(db)
    message_repo = SQLAlchemyMessageRepository(db)

    use_case = GetMessagesUseCase(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
    )

    try:
        messages = use_case.execute(
            conversation_id=conversation_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return [message_to_response(m, db) for m in messages]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Send a message in a conversation."""
    conversation_repo = SQLAlchemyConversationRepository(db)
    message_repo = SQLAlchemyMessageRepository(db)

    # Get conversation to find other participant
    conversation = conversation_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if not conversation.is_participant(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Check feature access for non-text messages
    message_type = MessageType(request.message_type)
    if message_type.requires_booking:
        session_repo = SessionRepositoryAdapter(db)
        feature_use_case = CheckFeatureAccessUseCase(session_repo=session_repo)
        other_user_id = conversation.get_other_participant_id(current_user.id)
        access = feature_use_case.execute(
            user_id=current_user.id,
            other_user_id=other_user_id,
        )

        if not access.can_send_message_type(message_type):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This feature requires a booked session",
            )

    # Send message
    use_case = SendMessageUseCase(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
    )

    try:
        message = use_case.execute(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            content=request.content,
            message_type=message_type,
            reply_to_id=request.reply_to_id,
        )
        db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return message_to_response(message, db)


@router.put("/conversations/{conversation_id}/read")
async def mark_messages_read(
    conversation_id: int,
    request: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Mark messages as read up to a certain message."""
    conversation_repo = SQLAlchemyConversationRepository(db)
    message_repo = SQLAlchemyMessageRepository(db)
    read_status_repo = SQLAlchemyReadStatusRepository(db)

    use_case = MarkMessagesReadUseCase(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        read_status_repo=read_status_repo,
    )

    try:
        updated_count = use_case.execute(
            conversation_id=conversation_id,
            user_id=current_user.id,
            message_id=request.message_id,
        )
        db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return {"updated_count": updated_count}


@router.get("/feature-access/{other_user_id}", response_model=FeatureAccessResponse)
async def get_feature_access(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Check what messaging features are available with another user."""
    session_repo = SessionRepositoryAdapter(db)

    use_case = CheckFeatureAccessUseCase(session_repo=session_repo)
    access = use_case.execute(
        user_id=current_user.id,
        other_user_id=other_user_id,
    )

    return FeatureAccessResponse(
        can_send_text=access.can_send_text,
        can_send_image=access.can_send_image,
        can_send_file=access.can_send_file,
        has_booking=access.has_booking,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_allow_inactive),
):
    """Get total unread message count for bell icon."""
    message_repo = SQLAlchemyMessageRepository(db)

    use_case = GetUnreadCountUseCase(message_repo=message_repo)
    count = use_case.execute(user_id=current_user.id)

    return UnreadCountResponse(unread_count=count)
