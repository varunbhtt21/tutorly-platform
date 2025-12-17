/**
 * Booking Confirmation Component
 * Shows success message after successful booking
 */

import React from 'react';
import { Link } from 'react-router-dom';
import {
  CheckCircle,
  Calendar,
  Clock,
  User,
  Video,
  ArrowRight,
  Home,
} from 'lucide-react';
import { Button } from '../UIComponents';

interface BookingConfirmationProps {
  sessionId: number;
  instructorName: string;
  instructorPhoto?: string;
  lessonDate: string;
  lessonTime: string;
  amountPaid: string;
  onClose?: () => void;
}

const BookingConfirmation: React.FC<BookingConfirmationProps> = ({
  sessionId,
  instructorName,
  instructorPhoto,
  lessonDate,
  lessonTime,
  amountPaid,
  onClose,
}) => {
  return (
    <div className="text-center max-w-md mx-auto py-8">
      {/* Success Icon */}
      <div className="w-20 h-20 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center animate-bounce-once">
        <CheckCircle size={48} className="text-green-600" />
      </div>

      {/* Title */}
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Booking Confirmed!
      </h2>
      <p className="text-gray-600 mb-8">
        Your trial lesson has been successfully booked.
      </p>

      {/* Booking Details Card */}
      <div className="bg-gradient-to-br from-primary-50 to-emerald-50 rounded-2xl p-6 mb-8 text-left">
        {/* Instructor */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-xl overflow-hidden bg-gray-200">
            {instructorPhoto ? (
              <img
                src={instructorPhoto}
                alt={instructorName}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-primary-100">
                <User size={28} className="text-primary-600" />
              </div>
            )}
          </div>
          <div>
            <p className="text-sm text-gray-500">Your Instructor</p>
            <p className="text-lg font-bold text-gray-900">{instructorName}</p>
          </div>
        </div>

        {/* Details Grid */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center">
              <Calendar size={18} className="text-primary-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Date</p>
              <p className="font-medium text-gray-900">{lessonDate}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center">
              <Clock size={18} className="text-primary-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Time</p>
              <p className="font-medium text-gray-900">{lessonTime}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center">
              <Video size={18} className="text-primary-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Session Type</p>
              <p className="font-medium text-gray-900">Online Video Call</p>
            </div>
          </div>
        </div>

        {/* Amount Paid */}
        <div className="mt-6 pt-4 border-t border-primary-200/50 flex items-center justify-between">
          <span className="text-gray-600">Amount Paid</span>
          <span className="text-xl font-bold text-green-600">{amountPaid}</span>
        </div>
      </div>

      {/* Confirmation ID */}
      <p className="text-sm text-gray-500 mb-6">
        Confirmation ID: <span className="font-mono font-medium">#{sessionId}</span>
      </p>

      {/* Info Note */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-8 text-left">
        <p className="text-sm text-blue-700">
          <strong>What's next?</strong> You'll receive a confirmation email with the meeting link.
          Make sure to join on time!
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Link to="/dashboard" className="flex-1">
          <Button variant="outline" className="w-full gap-2">
            <Home size={18} />
            Go to Dashboard
          </Button>
        </Link>
        <Link to="/my-lessons" className="flex-1">
          <Button className="w-full gap-2 bg-gradient-to-r from-emerald-500 to-green-600">
            View My Lessons
            <ArrowRight size={18} />
          </Button>
        </Link>
      </div>

      {/* Animation Styles */}
      <style>{`
        @keyframes bounce-once {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-bounce-once {
          animation: bounce-once 0.5s ease-out;
        }
      `}</style>
    </div>
  );
};

export default BookingConfirmation;
