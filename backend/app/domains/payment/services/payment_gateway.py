"""
Payment Gateway Interface (Port).

Defines the contract for payment gateway operations.
Implementations (adapters) will handle specific gateway integrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class GatewayOrder:
    """
    Value object representing a created gateway order.

    Contains all information needed by the frontend to
    complete the payment flow.
    """

    order_id: str           # Gateway's order reference
    amount: int             # Amount in smallest currency unit (paise)
    currency: str           # Currency code
    key: str               # Public key for frontend
    name: str              # Business name for display
    description: str       # Order description
    prefill_name: Optional[str] = None
    prefill_email: Optional[str] = None
    prefill_contact: Optional[str] = None
    notes: Optional[dict] = None


@dataclass
class GatewayVerificationResult:
    """
    Value object representing payment verification result.
    """

    is_valid: bool
    payment_id: str
    order_id: str
    signature: str
    error_message: Optional[str] = None
    payment_method: Optional[str] = None


@dataclass
class RefundResult:
    """
    Value object representing refund result.
    """

    is_success: bool
    refund_id: Optional[str] = None
    amount: Optional[int] = None
    error_message: Optional[str] = None


class IPaymentGateway(ABC):
    """
    Payment Gateway Interface (Port).

    Defines the contract for payment gateway integrations.
    Following the Ports & Adapters (Hexagonal) architecture pattern.

    Implementations:
    - RazorpayGateway (production)
    - MockGateway (testing)
    """

    @abstractmethod
    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        notes: Optional[dict] = None,
        prefill_name: Optional[str] = None,
        prefill_email: Optional[str] = None,
        prefill_contact: Optional[str] = None,
    ) -> GatewayOrder:
        """
        Create a payment order with the gateway.

        Args:
            amount: Payment amount (will be converted to smallest unit)
            currency: Currency code (e.g., "INR")
            receipt: Internal reference (e.g., payment ID)
            notes: Additional metadata
            prefill_name: Customer name for prefill
            prefill_email: Customer email for prefill
            prefill_contact: Customer phone for prefill

        Returns:
            GatewayOrder with order details for frontend

        Raises:
            PaymentGatewayError: If order creation fails
        """
        pass

    @abstractmethod
    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> GatewayVerificationResult:
        """
        Verify a payment signature.

        Args:
            order_id: Gateway's order reference
            payment_id: Gateway's payment reference
            signature: Signature to verify

        Returns:
            GatewayVerificationResult with verification status

        Raises:
            PaymentGatewayError: If verification fails
        """
        pass

    @abstractmethod
    def get_payment_details(self, payment_id: str) -> dict:
        """
        Get payment details from gateway.

        Args:
            payment_id: Gateway's payment reference

        Returns:
            Payment details from gateway

        Raises:
            PaymentGatewayError: If fetching fails
        """
        pass

    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        notes: Optional[dict] = None,
    ) -> RefundResult:
        """
        Refund a payment.

        Args:
            payment_id: Gateway's payment reference
            amount: Amount to refund (None for full refund)
            notes: Additional metadata

        Returns:
            RefundResult with refund status

        Raises:
            PaymentGatewayError: If refund fails
        """
        pass

    @abstractmethod
    def get_public_key(self) -> str:
        """
        Get the public/key ID for frontend integration.

        Returns:
            Public key for frontend
        """
        pass


class PaymentGatewayError(Exception):
    """Exception raised for payment gateway errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        gateway_response: Optional[dict] = None,
    ):
        self.message = message
        self.code = code
        self.gateway_response = gateway_response
        super().__init__(message)
