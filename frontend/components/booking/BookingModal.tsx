/**
 * Booking Modal Component
 * Full booking flow modal: Slot Selection -> Checkout -> Confirmation
 */

import React, { useState } from 'react';
import { X, ArrowLeft } from 'lucide-react';
import SlotSelector from './SlotSelector';
import BookingCheckout from './BookingCheckout';
import BookingConfirmation from './BookingConfirmation';
import { getMediaUrl } from '../../lib/axios';

interface Slot {
  id: number;
  start_at: string;
  end_at: string;
  duration_minutes: number;
  status: string;
}

type BookingStep = 'select_slot' | 'checkout' | 'confirmation';

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  instructorId: number;
  instructorName: string;
  instructorPhoto?: string;
  trialPrice: number;
  hourlyRate?: number;
}

const BookingModal: React.FC<BookingModalProps> = ({
  isOpen,
  onClose,
  instructorId,
  instructorName,
  instructorPhoto,
  trialPrice,
  hourlyRate,
}) => {
  const [step, setStep] = useState<BookingStep>('select_slot');
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [lessonType, setLessonType] = useState<'trial' | 'regular'>('trial');
  const [confirmedSessionId, setConfirmedSessionId] = useState<number | null>(null);

  if (!isOpen) return null;

  const handleSlotSelect = (slot: Slot) => {
    setSelectedSlot(slot);
    setStep('checkout');
  };

  const handlePaymentSuccess = (sessionId: number) => {
    setConfirmedSessionId(sessionId);
    setStep('confirmation');
  };

  const handleBack = () => {
    if (step === 'checkout') {
      setStep('select_slot');
    }
  };

  const handleClose = () => {
    // Reset state
    setStep('select_slot');
    setSelectedSlot(null);
    setConfirmedSessionId(null);
    onClose();
  };

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

  const getTitle = () => {
    switch (step) {
      case 'select_slot':
        return 'Book a Trial Lesson';
      case 'checkout':
        return 'Complete Payment';
      case 'confirmation':
        return 'Booking Confirmed';
      default:
        return 'Book a Lesson';
    }
  };

  const price = lessonType === 'trial' ? trialPrice : (hourlyRate || trialPrice);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={step !== 'confirmation' ? handleClose : undefined}
      />

      {/* Modal */}
      <div
        className={`
        relative bg-white rounded-2xl shadow-2xl overflow-hidden
        max-h-[90vh] overflow-y-auto animate-slideDown
        ${step === 'select_slot' ? 'w-full max-w-4xl mx-4' : 'w-full max-w-lg mx-4'}
      `}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-gray-100 bg-white">
          <div className="flex items-center gap-3">
            {step === 'checkout' && (
              <button
                onClick={handleBack}
                className="p-2 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
            )}
            <h2 className="text-lg font-bold text-gray-900">{getTitle()}</h2>
          </div>
          {step !== 'confirmation' && (
            <button
              onClick={handleClose}
              className="p-2 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <X size={20} className="text-gray-500" />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          {step === 'select_slot' && (
            <div>
              {/* Instructor Mini Card */}
              <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
                <div className="w-14 h-14 rounded-xl overflow-hidden bg-gray-200">
                  {instructorPhoto ? (
                    <img
                      src={getMediaUrl(instructorPhoto)}
                      alt={instructorName}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-primary-100 text-xl font-bold text-primary-600">
                      {instructorName.charAt(0)}
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{instructorName}</p>
                  <p className="text-sm text-gray-500">
                    Trial lesson: <span className="font-semibold text-green-600">₹{trialPrice}</span>
                  </p>
                </div>
              </div>

              {/* Slot Selector */}
              <SlotSelector
                instructorId={instructorId}
                onSlotSelect={handleSlotSelect}
                selectedSlotId={selectedSlot?.id}
              />
            </div>
          )}

          {step === 'checkout' && selectedSlot && (
            <BookingCheckout
              instructorId={instructorId}
              instructorName={instructorName}
              instructorPhoto={instructorPhoto ? getMediaUrl(instructorPhoto) : undefined}
              slot={selectedSlot}
              trialPrice={price}
              lessonType={lessonType}
              onSuccess={handlePaymentSuccess}
              onCancel={handleBack}
            />
          )}

          {step === 'confirmation' && selectedSlot && confirmedSessionId && (
            <BookingConfirmation
              sessionId={confirmedSessionId}
              instructorName={instructorName}
              instructorPhoto={instructorPhoto ? getMediaUrl(instructorPhoto) : undefined}
              lessonDate={formatDate(selectedSlot.start_at)}
              lessonTime={formatTime(selectedSlot.start_at)}
              amountPaid={`₹${price}`}
              onClose={handleClose}
            />
          )}
        </div>
      </div>

      {/* Animation Styles */}
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideDown {
          animation: slideDown 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default BookingModal;
