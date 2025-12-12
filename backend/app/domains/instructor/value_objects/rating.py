"""Rating value object."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Rating:
    """
    Rating value object.

    Immutable rating with score and review count.
    """

    average_score: Decimal
    total_reviews: int

    # Rating constraints
    MIN_SCORE = Decimal("0.0")
    MAX_SCORE = Decimal("5.0")

    def __post_init__(self):
        """Validate rating on creation."""
        if self.average_score < self.MIN_SCORE or self.average_score > self.MAX_SCORE:
            raise ValueError(f"Rating must be between {self.MIN_SCORE} and {self.MAX_SCORE}")

        if self.total_reviews < 0:
            raise ValueError("Total reviews cannot be negative")

    @classmethod
    def create_empty(cls) -> "Rating":
        """
        Create empty rating (no reviews yet).

        Returns:
            Rating with 0.0 score and 0 reviews
        """
        return cls(average_score=Decimal("0.0"), total_reviews=0)

    @classmethod
    def create(cls, average_score: float, total_reviews: int) -> "Rating":
        """
        Create Rating from float score.

        Args:
            average_score: Average rating score
            total_reviews: Total number of reviews

        Returns:
            Rating instance
        """
        return cls(
            average_score=Decimal(str(round(average_score, 2))),
            total_reviews=total_reviews
        )

    def add_review(self, new_score: float) -> "Rating":
        """
        Calculate new rating after adding a review.

        Args:
            new_score: New review score (1-5)

        Returns:
            New Rating instance with updated values
        """
        if new_score < 1.0 or new_score > 5.0:
            raise ValueError("Review score must be between 1.0 and 5.0")

        # Calculate new average
        total_score = float(self.average_score) * self.total_reviews
        new_total = total_score + new_score
        new_count = self.total_reviews + 1
        new_average = new_total / new_count

        return Rating.create(average_score=new_average, total_reviews=new_count)

    @property
    def has_reviews(self) -> bool:
        """Check if instructor has any reviews."""
        return self.total_reviews > 0

    @property
    def score_float(self) -> float:
        """Get average score as float."""
        return float(self.average_score)

    @property
    def is_highly_rated(self) -> bool:
        """Check if highly rated (4.5+)."""
        return self.average_score >= Decimal("4.5") and self.total_reviews >= 10

    @property
    def rating_category(self) -> str:
        """Get rating category."""
        if not self.has_reviews:
            return "No reviews"
        elif self.average_score >= Decimal("4.5"):
            return "Excellent"
        elif self.average_score >= Decimal("4.0"):
            return "Very Good"
        elif self.average_score >= Decimal("3.5"):
            return "Good"
        elif self.average_score >= Decimal("3.0"):
            return "Average"
        else:
            return "Below Average"

    def __str__(self) -> str:
        """String representation."""
        if not self.has_reviews:
            return "No reviews yet"
        return f"{self.average_score:.1f}/5.0 ({self.total_reviews} reviews)"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, Rating):
            return self.average_score == other.average_score and self.total_reviews == other.total_reviews
        return False

    def __hash__(self) -> int:
        """Make Rating hashable."""
        return hash((self.average_score, self.total_reviews))
