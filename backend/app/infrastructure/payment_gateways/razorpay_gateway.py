"""
Razorpay Payment Gateway Implementation.

Adapter for Razorpay payment gateway following the Ports & Adapters pattern.
"""

import hashlib
import hmac
from decimal import Decimal
from typing import Optional

import razorpay
from razorpay.errors import BadRequestError, ServerError

from app.domains.payment.services.payment_gateway import (
    IPaymentGateway,
    GatewayOrder,
    GatewayVerificationResult,
    RefundResult,
    PaymentGatewayError,
)


class RazorpayGateway(IPaymentGateway):
    """
    Razorpay Payment Gateway implementation.

    Handles all interactions with the Razorpay API for:
    - Creating payment orders
    - Verifying payment signatures
    - Processing refunds
    """

    def __init__(
        self,
        key_id: str,
        key_secret: str,
        business_name: str = "Tutorly",
    ):
        """
        Initialize Razorpay gateway.

        Args:
            key_id: Razorpay Key ID
            key_secret: Razorpay Key Secret
            business_name: Business name to display in checkout
        """
        self.key_id = key_id
        self.key_secret = key_secret
        self.business_name = business_name

        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(key_id, key_secret))

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
        Create a payment order with Razorpay.

        Args:
            amount: Payment amount (will be converted to paise)
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
        # Convert to paise (smallest currency unit for INR)
        amount_in_paise = int(amount * 100)

        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt,
            "notes": notes or {},
        }

        try:
            order = self.client.order.create(data=order_data)

            return GatewayOrder(
                order_id=order["id"],
                amount=amount_in_paise,
                currency=currency,
                key=self.key_id,
                name=self.business_name,
                description=notes.get("description", "Lesson Payment") if notes else "Lesson Payment",
                prefill_name=prefill_name,
                prefill_email=prefill_email,
                prefill_contact=prefill_contact,
                notes=notes,
            )

        except BadRequestError as e:
            raise PaymentGatewayError(
                message=f"Invalid order request: {str(e)}",
                code="BAD_REQUEST",
                gateway_response={"error": str(e)},
            )
        except ServerError as e:
            raise PaymentGatewayError(
                message=f"Razorpay server error: {str(e)}",
                code="SERVER_ERROR",
                gateway_response={"error": str(e)},
            )
        except Exception as e:
            raise PaymentGatewayError(
                message=f"Failed to create order: {str(e)}",
                code="UNKNOWN_ERROR",
                gateway_response={"error": str(e)},
            )

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> GatewayVerificationResult:
        """
        Verify a payment signature using Razorpay's signature verification.

        Args:
            order_id: Gateway's order reference
            payment_id: Gateway's payment reference
            signature: Signature to verify

        Returns:
            GatewayVerificationResult with verification status
        """
        try:
            # Generate the expected signature
            message = f"{order_id}|{payment_id}"
            expected_signature = hmac.new(
                key=self.key_secret.encode("utf-8"),
                msg=message.encode("utf-8"),
                digestmod=hashlib.sha256
            ).hexdigest()

            # Compare signatures
            is_valid = hmac.compare_digest(expected_signature, signature)

            if not is_valid:
                return GatewayVerificationResult(
                    is_valid=False,
                    payment_id=payment_id,
                    order_id=order_id,
                    signature=signature,
                    error_message="Invalid payment signature",
                )

            # Get payment details to extract method
            payment_details = self.get_payment_details(payment_id)
            payment_method = payment_details.get("method")

            return GatewayVerificationResult(
                is_valid=True,
                payment_id=payment_id,
                order_id=order_id,
                signature=signature,
                payment_method=payment_method,
            )

        except Exception as e:
            return GatewayVerificationResult(
                is_valid=False,
                payment_id=payment_id,
                order_id=order_id,
                signature=signature,
                error_message=f"Verification failed: {str(e)}",
            )

    def get_payment_details(self, payment_id: str) -> dict:
        """
        Get payment details from Razorpay.

        Args:
            payment_id: Gateway's payment reference

        Returns:
            Payment details from Razorpay

        Raises:
            PaymentGatewayError: If fetching fails
        """
        try:
            return self.client.payment.fetch(payment_id)
        except BadRequestError as e:
            raise PaymentGatewayError(
                message=f"Invalid payment ID: {str(e)}",
                code="BAD_REQUEST",
                gateway_response={"error": str(e)},
            )
        except Exception as e:
            raise PaymentGatewayError(
                message=f"Failed to fetch payment: {str(e)}",
                code="UNKNOWN_ERROR",
                gateway_response={"error": str(e)},
            )

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
            amount: Amount to refund in rupees (None for full refund)
            notes: Additional metadata

        Returns:
            RefundResult with refund status
        """
        try:
            refund_data = {}

            if amount is not None:
                # Convert to paise
                refund_data["amount"] = int(amount * 100)

            if notes:
                refund_data["notes"] = notes

            refund = self.client.payment.refund(payment_id, refund_data)

            return RefundResult(
                is_success=True,
                refund_id=refund.get("id"),
                amount=refund.get("amount"),
            )

        except BadRequestError as e:
            return RefundResult(
                is_success=False,
                error_message=f"Invalid refund request: {str(e)}",
            )
        except Exception as e:
            return RefundResult(
                is_success=False,
                error_message=f"Refund failed: {str(e)}",
            )

    def get_public_key(self) -> str:
        """
        Get the public/key ID for frontend integration.

        Returns:
            Razorpay Key ID
        """
        return self.key_id
