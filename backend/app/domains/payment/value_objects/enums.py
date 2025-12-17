"""
Payment Domain Enumerations.

Value objects representing the various states and types in the payment domain.
"""

from enum import Enum


class PaymentStatus(str, Enum):
    """
    Payment lifecycle status.

    Transitions:
    - PENDING -> PROCESSING (payment initiated with gateway)
    - PROCESSING -> COMPLETED (payment verified)
    - PROCESSING -> FAILED (payment failed/rejected)
    - COMPLETED -> REFUNDED (refund processed)
    - PENDING -> CANCELLED (user cancelled before payment)
    """
    PENDING = "pending"           # Payment created, awaiting gateway order
    PROCESSING = "processing"     # Payment initiated, awaiting completion
    COMPLETED = "completed"       # Payment verified and successful
    FAILED = "failed"             # Payment failed
    REFUNDED = "refunded"         # Payment refunded
    CANCELLED = "cancelled"       # Payment cancelled before completion


class PaymentMethod(str, Enum):
    """
    Supported payment methods.

    UPI and Cards are primary methods for Indian market via Razorpay.
    """
    UPI = "upi"                   # Unified Payments Interface
    CARD = "card"                 # Credit/Debit cards
    NETBANKING = "netbanking"     # Net banking
    WALLET = "wallet"             # Digital wallets (PayTM, etc.)


class PaymentGateway(str, Enum):
    """
    Supported payment gateways.

    Currently only Razorpay for Indian market.
    """
    RAZORPAY = "razorpay"
    MOCK = "mock"                 # For testing


class LessonType(str, Enum):
    """
    Type of lesson being booked.

    Trial lessons have discounted pricing.
    """
    TRIAL = "trial"               # First lesson with discounted rate
    REGULAR = "regular"           # Standard lesson at hourly rate
