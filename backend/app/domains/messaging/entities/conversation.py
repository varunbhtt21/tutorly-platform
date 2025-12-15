"""Conversation domain entity."""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from ..events import ConversationCreated


@dataclass
class Conversation:
    """
    Conversation aggregate root.

    Represents a chat conversation between two users (student and instructor).
    Rich domain entity with business logic and invariants.
    """

    # Identity
    id: Optional[int] = None

    # Participants
    participant_1_id: int = field(default=0)  # Initiator (usually student)
    participant_2_id: int = field(default=0)  # Recipient (usually instructor)

    # Last message tracking for efficient querying
    last_message_id: Optional[int] = None
    last_message_at: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Domain Events (not persisted)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Initialize domain invariants."""
        if not self.participant_1_id:
            raise ValueError("Participant 1 ID is required")
        if not self.participant_2_id:
            raise ValueError("Participant 2 ID is required")
        if self.participant_1_id == self.participant_2_id:
            raise ValueError("Cannot create conversation with self")

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        initiator_id: int,
        recipient_id: int,
    ) -> "Conversation":
        """
        Create a new conversation between two users.

        Args:
            initiator_id: User who started the conversation
            recipient_id: User who receives the conversation

        Returns:
            New Conversation instance
        """
        now = datetime.utcnow()

        conversation = cls(
            participant_1_id=initiator_id,
            participant_2_id=recipient_id,
            created_at=now,
            updated_at=now,
        )

        # Emit domain event
        conversation._add_domain_event(
            ConversationCreated(
                conversation_id=conversation.id,
                participant_1_id=initiator_id,
                participant_2_id=recipient_id,
                created_at=now,
            )
        )

        return conversation

    # ========================================================================
    # Business Logic
    # ========================================================================

    def is_participant(self, user_id: int) -> bool:
        """Check if user is a participant in this conversation."""
        return user_id in (self.participant_1_id, self.participant_2_id)

    def get_other_participant_id(self, user_id: int) -> int:
        """Get the other participant's ID."""
        if user_id == self.participant_1_id:
            return self.participant_2_id
        elif user_id == self.participant_2_id:
            return self.participant_1_id
        else:
            raise ValueError(f"User {user_id} is not a participant")

    def update_last_message(self, message_id: int, sent_at: datetime) -> None:
        """Update the last message reference."""
        self.last_message_id = message_id
        self.last_message_at = sent_at
        self.updated_at = datetime.utcnow()

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
        """Conversation equality based on ID."""
        if not isinstance(other, Conversation):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Make Conversation hashable."""
        return hash(self.id) if self.id else hash(id(self))
