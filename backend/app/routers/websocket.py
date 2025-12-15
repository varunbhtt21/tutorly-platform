"""
WebSocket API for Real-time Messaging.

Handles WebSocket connections for:
- Real-time message delivery
- Typing indicators
- Online presence
- Read receipts

Uses DDD use cases for business logic.
"""

import logging
from datetime import datetime
from typing import Dict, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import SessionLocal
from app.core.security import decode_token
from app.database.models import (
    Conversation as OrmConversation,
    User as UserModel,
    InstructorProfile,
)

# Domain imports
from app.domains.messaging.value_objects import MessageType
from app.domains.messaging.entities import Message

# Use case imports
from app.application.use_cases.messaging import (
    SendMessageUseCase,
    MarkMessagesReadUseCase,
)

# Repository imports
from app.infrastructure.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyMessageRepository,
    SQLAlchemyReadStatusRepository,
)


logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time messaging."""

    def __init__(self):
        # Map user_id to their WebSocket connection
        self.active_connections: Dict[int, WebSocket] = {}
        # Map conversation_id to set of user_ids currently viewing it
        self.conversation_viewers: Dict[int, Set[int]] = {}
        # Map user_id to set of conversation_ids they're viewing
        self.user_conversations: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept WebSocket connection and track user."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_conversations[user_id] = set()
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: int):
        """Remove WebSocket connection and clean up."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Remove user from all conversation viewers
        if user_id in self.user_conversations:
            for conv_id in self.user_conversations[user_id]:
                if conv_id in self.conversation_viewers:
                    self.conversation_viewers[conv_id].discard(user_id)
            del self.user_conversations[user_id]

        logger.info(f"User {user_id} disconnected from WebSocket")

    def join_conversation(self, user_id: int, conversation_id: int):
        """Mark user as viewing a conversation."""
        if conversation_id not in self.conversation_viewers:
            self.conversation_viewers[conversation_id] = set()
        self.conversation_viewers[conversation_id].add(user_id)

        if user_id in self.user_conversations:
            self.user_conversations[user_id].add(conversation_id)

    def leave_conversation(self, user_id: int, conversation_id: int):
        """Mark user as no longer viewing a conversation."""
        if conversation_id in self.conversation_viewers:
            self.conversation_viewers[conversation_id].discard(user_id)

        if user_id in self.user_conversations:
            self.user_conversations[user_id].discard(conversation_id)

    def is_user_online(self, user_id: int) -> bool:
        """Check if user is currently connected."""
        return user_id in self.active_connections

    def get_conversation_users(self, conversation_id: int) -> Set[int]:
        """Get users currently viewing a conversation."""
        return self.conversation_viewers.get(conversation_id, set())

    async def send_to_user(self, user_id: int, message: dict):
        """Send message to a specific user if connected."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send to user {user_id}: {e}")
                self.disconnect(user_id)
        return False

    async def broadcast_to_conversation(
        self,
        conversation_id: int,
        message: dict,
        exclude_user: Optional[int] = None
    ):
        """Send message to all users viewing a conversation."""
        viewers = self.get_conversation_users(conversation_id)
        for user_id in viewers:
            if user_id != exclude_user:
                await self.send_to_user(user_id, message)


# Global connection manager
manager = ConnectionManager()


# ============================================================================
# Helper Functions
# ============================================================================

def get_db_session() -> Session:
    """Get database session for WebSocket handlers."""
    return SessionLocal()


def verify_websocket_token(token: str) -> Optional[int]:
    """Verify JWT token and return user_id."""
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    return int(user_id) if user_id else None


def can_access_conversation(db: Session, user_id: int, conversation_id: int) -> bool:
    """Check if user is a participant in the conversation."""
    conv_repo = SQLAlchemyConversationRepository(db)
    conversation = conv_repo.get_by_id(conversation_id)
    if not conversation:
        return False
    return conversation.is_participant(user_id)


def get_other_participant_id(db: Session, conversation_id: int, user_id: int) -> Optional[int]:
    """Get the other participant's user ID in a conversation."""
    conv_repo = SQLAlchemyConversationRepository(db)
    conversation = conv_repo.get_by_id(conversation_id)
    if not conversation:
        return None
    return conversation.get_other_participant_id(user_id)


def get_user_basic_info(db: Session, user_id: int) -> Optional[dict]:
    """Get basic user info for message responses."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None

    profile_photo = None
    if user.role.value == "instructor":
        instructor_profile = db.query(InstructorProfile).filter(
            InstructorProfile.user_id == user_id
        ).first()
        if instructor_profile:
            profile_photo = instructor_profile.profile_photo_url

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profile_photo_url": profile_photo,
        "role": user.role.value,
    }


def message_to_dict(message: Message, db: Session) -> dict:
    """Convert domain Message to dict for WebSocket response."""
    sender = get_user_basic_info(db, message.sender_id)
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender": sender,
        "content": message.content,
        "message_type": message.message_type.value,
        "status": message.status.value,
        "reply_to_id": message.reply_to_id,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time messaging.

    Events from client:
    - join_conversation: { conversation_id }
    - leave_conversation: { conversation_id }
    - send_message: { conversation_id, content, message_type?, reply_to_id? }
    - typing_start: { conversation_id }
    - typing_stop: { conversation_id }
    - mark_read: { conversation_id, message_id }

    Events to client:
    - connected: { user_id }
    - new_message: { message }
    - message_sent: { message, temp_id }
    - message_delivered: { message_id }
    - message_read: { conversation_id, message_id, read_by }
    - user_typing: { conversation_id, user_id }
    - user_stopped_typing: { conversation_id, user_id }
    - user_online: { user_id }
    - user_offline: { user_id }
    - error: { message }
    """
    # Verify token
    user_id = verify_websocket_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    # Accept connection
    await manager.connect(websocket, user_id)

    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "user_id": user_id
    })

    # Notify contacts that user is online
    db = get_db_session()
    try:
        # Get all conversations for this user
        conversations = db.query(OrmConversation).filter(
            or_(
                OrmConversation.participant_1_id == user_id,
                OrmConversation.participant_2_id == user_id
            )
        ).all()

        # Notify other participants
        for conv in conversations:
            other_id = get_other_participant_id(db, conv.id, user_id)
            if other_id:
                await manager.send_to_user(other_id, {
                    "type": "user_online",
                    "user_id": user_id
                })
    finally:
        db.close()

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "join_conversation":
                await handle_join_conversation(user_id, data)

            elif event_type == "leave_conversation":
                await handle_leave_conversation(user_id, data)

            elif event_type == "send_message":
                await handle_send_message(user_id, data, websocket)

            elif event_type == "typing_start":
                await handle_typing_start(user_id, data)

            elif event_type == "typing_stop":
                await handle_typing_stop(user_id, data)

            elif event_type == "mark_read":
                await handle_mark_read(user_id, data)

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown event type: {event_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(user_id)

        # Notify contacts that user is offline
        db = get_db_session()
        try:
            conversations = db.query(OrmConversation).filter(
                or_(
                    OrmConversation.participant_1_id == user_id,
                    OrmConversation.participant_2_id == user_id
                )
            ).all()

            for conv in conversations:
                other_id = get_other_participant_id(db, conv.id, user_id)
                if other_id:
                    await manager.send_to_user(other_id, {
                        "type": "user_offline",
                        "user_id": user_id
                    })
        finally:
            db.close()


# ============================================================================
# Event Handlers
# ============================================================================

async def handle_join_conversation(user_id: int, data: dict):
    """Handle user joining a conversation view."""
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        return

    db = get_db_session()
    try:
        if can_access_conversation(db, user_id, conversation_id):
            manager.join_conversation(user_id, conversation_id)
            logger.info(f"User {user_id} joined conversation {conversation_id}")
    finally:
        db.close()


async def handle_leave_conversation(user_id: int, data: dict):
    """Handle user leaving a conversation view."""
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        return

    manager.leave_conversation(user_id, conversation_id)
    logger.info(f"User {user_id} left conversation {conversation_id}")


async def handle_send_message(user_id: int, data: dict, websocket: WebSocket):
    """Handle sending a new message using DDD use case."""
    conversation_id = data.get("conversation_id")
    content = data.get("content")
    message_type_str = data.get("message_type", "text")
    reply_to_id = data.get("reply_to_id")
    temp_id = data.get("temp_id")  # Client-side temporary ID for optimistic UI

    if not conversation_id or not content:
        await websocket.send_json({
            "type": "error",
            "message": "Missing conversation_id or content"
        })
        return

    db = get_db_session()
    try:
        # Create repositories
        conversation_repo = SQLAlchemyConversationRepository(db)
        message_repo = SQLAlchemyMessageRepository(db)

        # Verify access
        conversation = conversation_repo.get_by_id(conversation_id)
        if not conversation or not conversation.is_participant(user_id):
            await websocket.send_json({
                "type": "error",
                "message": "Access denied"
            })
            return

        # Use the SendMessage use case
        use_case = SendMessageUseCase(
            conversation_repo=conversation_repo,
            message_repo=message_repo,
        )

        message_type = MessageType(message_type_str)

        message = use_case.execute(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=content,
            message_type=message_type,
            reply_to_id=reply_to_id,
        )

        db.commit()

        # Build message response
        message_data = message_to_dict(message, db)

        # Send confirmation to sender
        await websocket.send_json({
            "type": "message_sent",
            "message": message_data,
            "temp_id": temp_id
        })

        # Send to other participant
        other_id = conversation.get_other_participant_id(user_id)
        if other_id:
            sent = await manager.send_to_user(other_id, {
                "type": "new_message",
                "message": message_data
            })

            # Update status to DELIVERED if recipient is online
            if sent:
                message.mark_as_delivered()
                message_repo.update(message)
                db.commit()

                # Notify sender of delivery
                await websocket.send_json({
                    "type": "message_delivered",
                    "message_id": message.id
                })

    except ValueError as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        db.close()


async def handle_typing_start(user_id: int, data: dict):
    """Handle typing start indicator."""
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        return

    db = get_db_session()
    try:
        if can_access_conversation(db, user_id, conversation_id):
            other_id = get_other_participant_id(db, conversation_id, user_id)
            if other_id:
                await manager.send_to_user(other_id, {
                    "type": "user_typing",
                    "conversation_id": conversation_id,
                    "user_id": user_id
                })
    finally:
        db.close()


async def handle_typing_stop(user_id: int, data: dict):
    """Handle typing stop indicator."""
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        return

    db = get_db_session()
    try:
        if can_access_conversation(db, user_id, conversation_id):
            other_id = get_other_participant_id(db, conversation_id, user_id)
            if other_id:
                await manager.send_to_user(other_id, {
                    "type": "user_stopped_typing",
                    "conversation_id": conversation_id,
                    "user_id": user_id
                })
    finally:
        db.close()


async def handle_mark_read(user_id: int, data: dict):
    """Handle marking messages as read using DDD use case."""
    conversation_id = data.get("conversation_id")
    message_id = data.get("message_id")

    if not conversation_id or not message_id:
        return

    db = get_db_session()
    try:
        # Create repositories
        conversation_repo = SQLAlchemyConversationRepository(db)
        message_repo = SQLAlchemyMessageRepository(db)
        read_status_repo = SQLAlchemyReadStatusRepository(db)

        # Use the MarkMessagesRead use case
        use_case = MarkMessagesReadUseCase(
            conversation_repo=conversation_repo,
            message_repo=message_repo,
            read_status_repo=read_status_repo,
        )

        use_case.execute(
            conversation_id=conversation_id,
            user_id=user_id,
            message_id=message_id,
        )

        db.commit()

        # Notify sender
        other_id = get_other_participant_id(db, conversation_id, user_id)
        if other_id:
            await manager.send_to_user(other_id, {
                "type": "message_read",
                "conversation_id": conversation_id,
                "message_id": message_id,
                "read_by": user_id
            })

    except ValueError:
        pass  # Silently ignore access errors for mark_read
    finally:
        db.close()


# ============================================================================
# Utility Endpoint for Online Status
# ============================================================================

@router.get("/online/{user_id}")
async def check_user_online(user_id: int):
    """Check if a specific user is currently online."""
    return {"user_id": user_id, "online": manager.is_user_online(user_id)}
