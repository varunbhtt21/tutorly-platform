/**
 * Booking Checkout Component
 * Handles the payment flow with Razorpay integration
 */

import React, { useState, useEffect } from 'react';
import {
  Clock,
  Calendar,
  User,
  CreditCard,
  Shield,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { Button } from '../UIComponents';
import PaymentOptions from './PaymentOptions';
import api from '../../lib/axios';

declare global {
  interface Window {
    Razorpay: any;
  }
}

interface Slot {
  id: number | null; // null for dynamically generated recurring slots
  start_at: string;
  end_at: string;
  duration_minutes: number;
  availability_rule_id?: number | null;
  is_recurring?: boolean;
}

interface BookingCheckoutProps {
  instructorId: number;
  instructorName: string;
  instructorPhoto?: string;
  slot: Slot;
  trialPrice: number;
  lessonType?: 'trial' | 'regular';
  onSuccess: (sessionId: number) => void;
  onCancel: () => void;
}

type PaymentMethod = 'upi' | 'card' | 'netbanking' | 'wallet';

const BookingCheckout: React.FC<BookingCheckoutProps> = ({
  instructorId,
  instructorName,
  instructorPhoto,
  slot,
  trialPrice,
  lessonType = 'trial',
  onSuccess,
  onCancel,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('upi');
  const [razorpayLoaded, setRazorpayLoaded] = useState(false);

  // Load Razorpay script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => setRazorpayLoaded(true);
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const handlePayment = async () => {
    if (!razorpayLoaded) {
      setError('Payment system is loading. Please try again.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Step 1: Initiate booking and get Razorpay order
      // For recurring slots (no slot_id), we pass the availability_rule_id and slot times
      // The backend will create the booking slot on-the-fly
      const bookingPayload: Record<string, unknown> = {
        instructor_id: instructorId,
        lesson_type: lessonType,
      };

      if (slot.id !== null) {
        // One-time slot with existing slot_id
        bookingPayload.slot_id = slot.id;
      } else {
        // Recurring slot - pass availability rule and time info
        bookingPayload.availability_rule_id = slot.availability_rule_id;
        bookingPayload.start_at = slot.start_at;
        bookingPayload.end_at = slot.end_at;
        bookingPayload.duration_minutes = slot.duration_minutes;
      }

      const initiateResponse = await api.post('/booking/initiate', bookingPayload);

      const {
        payment_id,
        razorpay_order_id,
        razorpay_key,
        amount,
        currency,
        description,
      } = initiateResponse.data;

      // Step 2: Open Razorpay checkout
      const options = {
        key: razorpay_key,
        amount: amount,
        currency: currency,
        name: 'Tutorly',
        description: description,
        order_id: razorpay_order_id,
        prefill: {
          // You can prefill user info here
        },
        handler: async (response: any) => {
          // Step 3: Verify payment
          try {
            const verifyResponse = await api.post('/booking/verify', {
              payment_id: payment_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verifyResponse.data.success) {
              onSuccess(verifyResponse.data.session_id);
            } else {
              setError(verifyResponse.data.message || 'Payment verification failed');
            }
          } catch (verifyError: any) {
            setError(
              verifyError.response?.data?.detail || 'Payment verification failed'
            );
          }
          setLoading(false);
        },
        modal: {
          ondismiss: () => {
            setLoading(false);
          },
        },
        theme: {
          color: '#10b981',
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.on('payment.failed', (response: any) => {
        setError(response.error.description || 'Payment failed');
        setLoading(false);
      });
      razorpay.open();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate payment');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Order Summary */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden mb-6">
        <div className="p-6 bg-gradient-to-r from-primary-50 to-emerald-50 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Booking Summary
          </h3>

          {/* Instructor Info */}
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 rounded-xl overflow-hidden bg-gray-200">
              {instructorPhoto ? (
                <img
                  src={instructorPhoto}
                  alt={instructorName}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-primary-100">
                  <User size={24} className="text-primary-600" />
                </div>
              )}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{instructorName}</p>
              <p className="text-sm text-gray-500">
                {lessonType === 'trial' ? 'Trial Lesson' : 'Regular Lesson'}
              </p>
            </div>
          </div>

          {/* Date & Time */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2 bg-white/80 rounded-xl p-3">
              <Calendar size={18} className="text-primary-500" />
              <div>
                <p className="text-xs text-gray-500">Date</p>
                <p className="text-sm font-medium text-gray-900">
                  {formatDate(slot.start_at)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-white/80 rounded-xl p-3">
              <Clock size={18} className="text-primary-500" />
              <div>
                <p className="text-xs text-gray-500">Time</p>
                <p className="text-sm font-medium text-gray-900">
                  {formatTime(slot.start_at)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Price */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">
              {lessonType === 'trial' ? 'Trial lesson' : `${slot.duration_minutes} min lesson`}
            </span>
            <span className="text-2xl font-bold text-gray-900">
              ₹{trialPrice}
            </span>
          </div>
        </div>

        {/* Payment Options */}
        <div className="p-6">
          <PaymentOptions
            selectedMethod={paymentMethod}
            onMethodSelect={setPaymentMethod}
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-xl">
          <AlertCircle size={18} className="text-red-500" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button
          variant="outline"
          onClick={onCancel}
          className="flex-1"
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          onClick={handlePayment}
          disabled={loading || !razorpayLoaded}
          className="flex-1 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 shadow-lg shadow-emerald-500/30"
        >
          {loading ? (
            <>
              <Loader2 size={18} className="animate-spin mr-2" />
              Processing...
            </>
          ) : (
            <>
              <CreditCard size={18} className="mr-2" />
              Pay ₹{trialPrice}
            </>
          )}
        </Button>
      </div>

      {/* Security Badge */}
      <div className="mt-4 flex items-center justify-center gap-2 text-gray-500">
        <Shield size={14} />
        <span className="text-xs">Secure payment powered by Razorpay</span>
      </div>
    </div>
  );
};

export default BookingCheckout;
