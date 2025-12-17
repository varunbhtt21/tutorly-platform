"""Money value object for wallet transactions."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


@dataclass(frozen=True)
class Money:
    """
    Immutable value object representing monetary amount.

    Encapsulates currency validation and arithmetic operations
    while maintaining precision with Decimal.
    """

    amount: Decimal
    currency: str = "INR"

    # Constraints
    MIN_AMOUNT = Decimal("0.00")
    MAX_AMOUNT = Decimal("999999999.99")
    SUPPORTED_CURRENCIES = ("INR", "USD")  # INR is primary, USD as fallback

    def __post_init__(self):
        """Validate money on construction."""
        # Validate amount type
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        # Validate amount range
        if self.amount < self.MIN_AMOUNT:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        if self.amount > self.MAX_AMOUNT:
            raise ValueError(f"Amount exceeds maximum: {self.amount}")

        # Validate currency
        if self.currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.currency}")

        # Round to 2 decimal places
        rounded = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", rounded)

    @classmethod
    def create(
        cls, amount: Union[float, int, str, Decimal], currency: str = "INR"
    ) -> "Money":
        """
        Factory method to create Money from various types.

        Args:
            amount: The monetary amount
            currency: Currency code (default USD)

        Returns:
            Money instance
        """
        return cls(amount=Decimal(str(amount)), currency=currency)

    @classmethod
    def zero(cls, currency: str = "INR") -> "Money":
        """Create zero amount Money."""
        return cls(amount=Decimal("0.00"), currency=currency)

    def add(self, other: "Money") -> "Money":
        """
        Add two Money amounts.

        Args:
            other: Money to add

        Returns:
            New Money with sum

        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} vs {other.currency}"
            )
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        """
        Subtract Money amount.

        Args:
            other: Money to subtract

        Returns:
            New Money with difference

        Raises:
            ValueError: If currencies don't match or result is negative
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency} vs {other.currency}"
            )
        result = self.amount - other.amount
        if result < 0:
            raise ValueError(f"Insufficient funds: {self.amount} - {other.amount}")
        return Money(amount=result, currency=self.currency)

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == Decimal("0.00")

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > Decimal("0.00")

    @property
    def as_float(self) -> float:
        """Get amount as float for JSON serialization."""
        return float(self.amount)

    def __str__(self) -> str:
        """Format as currency string."""
        symbol = "₹" if self.currency == "INR" else "$"
        return f"{symbol}{self.amount:.2f} {self.currency}"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Money(amount={self.amount}, currency='{self.currency}')"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, Money):
            return self.amount == other.amount and self.currency == other.currency
        return False

    def __lt__(self, other: "Money") -> bool:
        """Less than comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount >= other.amount

    def __hash__(self) -> int:
        """Make Money hashable."""
        return hash((self.amount, self.currency))
