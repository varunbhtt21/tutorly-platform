/**
 * Availability Form Component
 * Form for adding recurring or one-time availability slots
 */

import React, { useState } from 'react';
import { Clock, Plus, X } from 'lucide-react';
import { getDayName } from '../../services/calendarAPI';

interface AvailabilityFormProps {
  onSubmitRecurring: (data: {
    day_of_week: number;
    start_time: string;
    end_time: string;
    slot_duration_minutes: number;
    break_minutes: number;
  }) => Promise<void>;
  onSubmitOneTime: (data: {
    specific_date: string;
    start_time: string;
    end_time: string;
    slot_duration_minutes: number;
    break_minutes: number;
  }) => Promise<void>;
  isLoading?: boolean;
}

export const AvailabilityForm: React.FC<AvailabilityFormProps> = ({
  onSubmitRecurring,
  onSubmitOneTime,
  isLoading = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [type, setType] = useState<'recurring' | 'one_time'>('recurring');
  const [dayOfWeek, setDayOfWeek] = useState(0);
  const [specificDate, setSpecificDate] = useState('');
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('17:00');
  const [slotDuration, setSlotDuration] = useState(50);
  const [breakDuration, setBreakDuration] = useState(10);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (startTime >= endTime) {
      setError('End time must be after start time');
      return;
    }

    if (type === 'one_time' && !specificDate) {
      setError('Please select a date');
      return;
    }

    try {
      if (type === 'recurring') {
        await onSubmitRecurring({
          day_of_week: dayOfWeek,
          start_time: startTime,
          end_time: endTime,
          slot_duration_minutes: slotDuration,
          break_minutes: breakDuration,
        });
      } else {
        await onSubmitOneTime({
          specific_date: specificDate,
          start_time: startTime,
          end_time: endTime,
          slot_duration_minutes: slotDuration,
          break_minutes: breakDuration,
        });
      }
      // Reset and close
      setIsOpen(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Failed to add availability');
    }
  };

  const resetForm = () => {
    setType('recurring');
    setDayOfWeek(0);
    setSpecificDate('');
    setStartTime('09:00');
    setEndTime('17:00');
    setSlotDuration(50);
    setBreakDuration(10);
    setError('');
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        <Plus className="h-5 w-5" />
        Add Availability
      </button>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Clock className="h-5 w-5 text-blue-600" />
          Add Availability
        </h3>
        <button
          onClick={() => {
            setIsOpen(false);
            resetForm();
          }}
          className="p-1 hover:bg-gray-100 rounded-full"
        >
          <X className="h-5 w-5 text-gray-400" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Availability Type
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                checked={type === 'recurring'}
                onChange={() => setType('recurring')}
                className="mr-2 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">Recurring Weekly</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                checked={type === 'one_time'}
                onChange={() => setType('one_time')}
                className="mr-2 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">One Time</span>
            </label>
          </div>
        </div>

        {/* Day/Date Selection */}
        {type === 'recurring' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Day of Week
            </label>
            <select
              value={dayOfWeek}
              onChange={(e) => setDayOfWeek(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Array.from({ length: 7 }, (_, i) => (
                <option key={i} value={i}>
                  {getDayName(i)}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date
            </label>
            <input
              type="date"
              value={specificDate}
              onChange={(e) => setSpecificDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        {/* Time Range */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Time
            </label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Time
            </label>
            <input
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Slot Configuration */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Slot Duration (minutes)
            </label>
            <select
              value={slotDuration}
              onChange={(e) => setSlotDuration(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={25}>25 minutes</option>
              <option value={50}>50 minutes</option>
              <option value={80}>80 minutes</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Break Between (minutes)
            </label>
            <select
              value={breakDuration}
              onChange={(e) => setBreakDuration(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={0}>No break</option>
              <option value={5}>5 minutes</option>
              <option value={10}>10 minutes</option>
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
            </select>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => {
              setIsOpen(false);
              resetForm();
            }}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Adding...' : 'Add Availability'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AvailabilityForm;
