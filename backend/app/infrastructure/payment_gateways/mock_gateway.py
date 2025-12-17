"""
Mock Payment Gateway Implementation.

Used for testing and development without actual payment processing.
"""

import hashlib
import uuid
from decimal import Decimal
from typing import Optional

from app.domains.payment.services.payment_gateway import (
    IPaymentGateway,
    GatewayOrder,
    GatewayVerificationResult,
    RefundResult,
)


class MockGateway(IPaymentGateway):
    """
    Mock Payment Gateway for testing.

    Simulates payment gateway behavior without actual transactions.
    """

    def __init__(self, key_id: str = "mock_key_id"):
        """
        Initialize mock gateway.

        Args:
            key_id: Mock key ID
        """
        self.key_id = key_id
        self._orders: dict = {}
        self._payments: dict = {}

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
        Create a mock payment order.

        Args:
            amount: Payment amount
            currency: Currency code
            receipt: Internal reference
            notes: Additional metadata
            prefill_name: Customer name
            prefill_email: Customer email
            prefill_contact: Customer phone

        Returns:
            GatewayOrder with mock order details
        """
        order_id = f"order_mock_{uuid.uuid4().hex[:16]}"
        amount_in_paise = int(amount * 100)

        self._orders[order_id] = {
            "id": order_id,
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt,
            "status": "created",
            "notes": notes or {},
        }

        return GatewayOrder(
            order_id=order_id,
            amount=amount_in_paise,
            currency=currency,
            key=self.key_id,
            name="Tutorly (Test)",
            description=notes.get("description", "Test Payment") if notes else "Test Payment",
            prefill_name=prefill_name,
            prefill_email=prefill_email,
            prefill_contact=prefill_contact,
            notes=notes,
        )

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> GatewayVerificationResult:
        """
        Verify a mock payment.

        In mock mode, always returns valid if signature starts with "mock_sig_".

        Args:
            order_id: Order reference
            payment_id: Payment reference
            signature: Signature to verify

        Returns:
            GatewayVerificationResult
        """
        # For mock, accept any signature starting with "mock_sig_"
        is_valid = signature.startswith("mock_sig_") or signature == "test_signature"

        if is_valid:
            # Store the payment
            self._payments[payment_id] = {
                "id": payment_id,
                "order_id": order_id,
                "status": "captured",
                "method": "mock",
            }

            if order_id in self._orders:
                self._orders[order_id]["status"] = "paid"

        return GatewayVerificationResult(
            is_valid=is_valid,
            payment_id=payment_id,
            order_id=order_id,
            signature=signature,
            payment_method="mock" if is_valid else None,
            error_message=None if is_valid else "Invalid mock signature",
        )

    def get_payment_details(self, payment_id: str) -> dict:
        """
        Get mock payment details.

        Args:
            payment_id: Payment reference

        Returns:
            Mock payment details
        """
        if payment_id in self._payments:
            return self._payments[payment_id]

        # Return default mock payment
        return {
            "id": payment_id,
            "status": "captured",
            "method": "mock",
            "amount": 10000,
            "currency": "INR",
        }

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        notes: Optional[dict] = None,
    ) -> RefundResult:
        """
        Process mock refund.

        Args:
            payment_id: Payment reference
            amount: Amount to refund
            notes: Additional metadata

        Returns:
            RefundResult (always successful in mock)
        """
        refund_id = f"rfnd_mock_{uuid.uuid4().hex[:16]}"

        return RefundResult(
            is_success=True,
            refund_id=refund_id,
            amount=int(amount * 100) if amount else None,
        )

    def get_public_key(self) -> str:
        """
        Get mock public key.

        Returns:
            Mock key ID
        """
        return self.key_id

    # Helper methods for testing

    def simulate_payment(self, order_id: str) -> tuple[str, str]:
        """
        Simulate a successful payment for testing.

        Args:
            order_id: Order to pay

        Returns:
            Tuple of (payment_id, signature)
        """
        payment_id = f"pay_mock_{uuid.uuid4().hex[:16]}"
        signature = f"mock_sig_{hashlib.sha256(f'{order_id}|{payment_id}'.encode()).hexdigest()[:32]}"

        self._payments[payment_id] = {
            "id": payment_id,
            "order_id": order_id,
            "status": "captured",
            "method": "mock",
        }

        return payment_id, signature
