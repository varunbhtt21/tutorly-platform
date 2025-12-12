"""PricingUpdated domain event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PricingUpdated:
    """
    Domain event: Instructor pricing has been updated.

    Emitted when an instructor changes their lesson pricing.
    Can trigger:
    - Update instructor pricing in search index
    - Notify existing students of price change
    - Adjust pricing for future bookings
    - Log pricing change history
    - Log analytics event
    """

    instructor_id: int
    user_id: int
    old_regular_price: Optional[float]
    new_regular_price: float
    updated_at: datetime

    def __str__(self) -> str:
        """String representation."""
        return f"PricingUpdated(instructor_id={self.instructor_id}, new_price={self.new_regular_price})"
