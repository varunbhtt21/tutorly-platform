"""Pricing value object."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Pricing:
    """
    Instructor pricing value object.

    Ensures pricing rules and constraints.
    Immutable - cannot be changed after creation.
    """

    regular_session_price: Decimal  # 50-minute session
    trial_session_price: Optional[Decimal] = None  # 25-minute trial (optional)

    # Pricing constraints
    MIN_REGULAR_PRICE = Decimal("5.00")
    MAX_REGULAR_PRICE = Decimal("200.00")
    MIN_TRIAL_PRICE = Decimal("1.00")
    MAX_TRIAL_PRICE = Decimal("100.00")

    def __post_init__(self):
        """Validate pricing on creation."""
        # Validate regular session price
        if self.regular_session_price < self.MIN_REGULAR_PRICE:
            raise ValueError(f"Regular session price must be at least ${self.MIN_REGULAR_PRICE}")

        if self.regular_session_price > self.MAX_REGULAR_PRICE:
            raise ValueError(f"Regular session price must not exceed ${self.MAX_REGULAR_PRICE}")

        # Validate trial session price if provided
        if self.trial_session_price is not None:
            if self.trial_session_price < self.MIN_TRIAL_PRICE:
                raise ValueError(f"Trial session price must be at least ${self.MIN_TRIAL_PRICE}")

            if self.trial_session_price > self.MAX_TRIAL_PRICE:
                raise ValueError(f"Trial session price must not exceed ${self.MAX_TRIAL_PRICE}")

            # Trial should be cheaper than regular
            if self.trial_session_price >= self.regular_session_price:
                raise ValueError("Trial session price must be less than regular session price")

    @classmethod
    def create(cls, regular_price: float, trial_price: Optional[float] = None) -> "Pricing":
        """
        Create Pricing from float values.

        Args:
            regular_price: Regular session price
            trial_price: Optional trial session price

        Returns:
            Pricing instance
        """
        return cls(
            regular_session_price=Decimal(str(regular_price)),
            trial_session_price=Decimal(str(trial_price)) if trial_price else None
        )

    @property
    def has_trial(self) -> bool:
        """Check if trial pricing is available."""
        return self.trial_session_price is not None

    @property
    def regular_price_float(self) -> float:
        """Get regular price as float."""
        return float(self.regular_session_price)

    @property
    def trial_price_float(self) -> Optional[float]:
        """Get trial price as float."""
        return float(self.trial_session_price) if self.trial_session_price else None

    def calculate_session_price(self, is_trial: bool = False) -> Decimal:
        """
        Calculate price for a session.

        Args:
            is_trial: Whether this is a trial session

        Returns:
            Session price
        """
        if is_trial:
            if not self.has_trial:
                raise ValueError("Trial pricing not available")
            return self.trial_session_price
        return self.regular_session_price

    def __str__(self) -> str:
        """String representation."""
        if self.has_trial:
            return f"${self.regular_session_price}/session (Trial: ${self.trial_session_price})"
        return f"${self.regular_session_price}/session"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, Pricing):
            return (
                self.regular_session_price == other.regular_session_price
                and self.trial_session_price == other.trial_session_price
            )
        return False

    def __hash__(self) -> int:
        """Make Pricing hashable."""
        return hash((self.regular_session_price, self.trial_session_price))
