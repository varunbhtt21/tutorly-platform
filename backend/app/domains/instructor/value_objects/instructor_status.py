"""InstructorStatus value object."""

from enum import Enum


class InstructorStatus(str, Enum):
    """
    Instructor profile status enumeration.

    Represents the lifecycle stages of an instructor's profile.
    """

    DRAFT = "draft"  # Initial state, onboarding not complete
    PENDING_REVIEW = "pending_review"  # Submitted for admin review
    VERIFIED = "verified"  # Approved and can accept bookings
    REJECTED = "rejected"  # Not approved by admin
    SUSPENDED = "suspended"  # Temporarily suspended by admin

    def __str__(self) -> str:
        """String representation."""
        return self.value

    @property
    def is_draft(self) -> bool:
        """Check if status is draft."""
        return self == InstructorStatus.DRAFT

    @property
    def is_pending_review(self) -> bool:
        """Check if status is pending review."""
        return self == InstructorStatus.PENDING_REVIEW

    @property
    def is_verified(self) -> bool:
        """Check if status is verified."""
        return self == InstructorStatus.VERIFIED

    @property
    def is_rejected(self) -> bool:
        """Check if status is rejected."""
        return self == InstructorStatus.REJECTED

    @property
    def is_suspended(self) -> bool:
        """Check if status is suspended."""
        return self == InstructorStatus.SUSPENDED

    def can_accept_bookings(self) -> bool:
        """Check if instructor can accept bookings."""
        return self == InstructorStatus.VERIFIED

    def can_submit_for_review(self) -> bool:
        """Check if can submit for review."""
        return self in (InstructorStatus.DRAFT, InstructorStatus.REJECTED)

    def can_be_verified(self) -> bool:
        """Check if can be verified."""
        return self == InstructorStatus.PENDING_REVIEW

    def can_be_suspended(self) -> bool:
        """Check if can be suspended."""
        return self == InstructorStatus.VERIFIED
